from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import MedicalRecordRequest, ArchiveAccessLog
from backend.users.models import GeneralDoctorProfile, NurseProfile, PatientProfile
from .serializers import MedicalRecordRequestSerializer, CreateMedicalRecordRequestSerializer
from .pdf_service import generate_records_pdf, encrypt_pdf_aes256, send_encrypted_pdf_to_patient

User = get_user_model()


def _broadcast_notification(user_ids, payload):
    try:
        channel_layer = get_channel_layer()
        for uid in set([uid for uid in user_ids if uid]):
            async_to_sync(channel_layer.group_send)(
                f'messaging_{uid}',
                {
                    'type': 'notification',
                    'notification': payload
                }
            )
    except Exception:
        # Non-blocking; logging can be added if needed
        pass


def _build_password(doctor_user: User, patient_user: User) -> str:
    # First letter of doctor's first name and last name (uppercase), + patient birth year
    # Example: EI2001
    first_name = ''
    last_name = ''
    if getattr(doctor_user, 'full_name', None):
        parts = str(doctor_user.full_name).strip().split()
        if parts:
            first_name = parts[0]
            last_name = parts[-1] if len(parts) > 1 else ''
    else:
        first_name = getattr(doctor_user, 'first_name', '')
        last_name = getattr(doctor_user, 'last_name', '')

    d1 = (first_name[:1] or 'X').upper()
    d2 = (last_name[:1] or 'X').upper()
    birth_year = ''
    dob = getattr(patient_user, 'date_of_birth', None)
    if dob:
        birth_year = str(dob.year)
    else:
        birth_year = '0000'
    return f"{d1}{d2}{birth_year}"


def _collect_records(patient_user: User, requested_records):
    # For now, pull from PatientProfile structured fields
    data = {}
    try:
        profile = patient_user.patient_profile
    except PatientProfile.DoesNotExist:
        profile = None
    if not profile:
        return data

    # Map possible keys to profile attributes
    mapping = {
        'intake_assessment': 'intake_assessment',
        'graphic_flow_sheets': 'graphic_flow_sheets',
        'mar': 'medication_administration_record',
        'education_records': 'patient_education_records',
        'discharge_summary': 'discharge_summary',
        'history_physical': 'history_and_physical',
        'progress_notes': 'progress_notes',
        'provider_orders': 'provider_order_sheets',
        'operative_reports': 'operative_procedure_reports',
    }
    # If requested_records is empty, include a basic summary
    keys = list(mapping.keys()) if not requested_records else [k for k in mapping.keys() if requested_records.get(k)]
    for key in keys:
        attr = mapping[key]
        data[key] = getattr(profile, attr, None)
    # Always include minimal demographics
    data['patient'] = {
        'full_name': getattr(patient_user, 'full_name', ''),
        'email': getattr(patient_user, 'email', ''),
        'date_of_birth': str(getattr(patient_user, 'date_of_birth', '') or ''),
    }
    return data


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def medical_requests(request):
    user: User = request.user

    if request.method == 'GET':
        # Role-based visibility
        qs = MedicalRecordRequest.objects.none()
        role = getattr(user, 'role', None)
        if role == 'patient':
            qs = MedicalRecordRequest.objects.filter(patient=user)
        elif role == 'nurse':
            try:
                nurse = user.nurse_profile
                qs = MedicalRecordRequest.objects.filter(primary_nurse=nurse)
            except NurseProfile.DoesNotExist:
                qs = MedicalRecordRequest.objects.filter(requested_by=user)
        elif role == 'doctor':
            # Use correct reverse accessor for doctor profile
            doc = getattr(user, 'doctor_profile', None)
            if doc:
                qs = MedicalRecordRequest.objects.filter(attending_doctor=doc)
            else:
                qs = MedicalRecordRequest.objects.filter(approved_by=user)
        else:
            # Admin or other roles see their own initiated
            qs = MedicalRecordRequest.objects.filter(requested_by=user)

        serializer = MedicalRecordRequestSerializer(qs.order_by('-created_at'), many=True, context={'request': request})
        return Response(serializer.data)

    # POST create
    serializer = CreateMedicalRecordRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    with transaction.atomic():
        patient = User.objects.get(id=data['patient_id'])
        attending_doctor = None
        primary_nurse = None
        if data.get('attending_doctor_id'):
            attending_doctor = GeneralDoctorProfile.objects.filter(id=data['attending_doctor_id']).first()

        # Auto-derive nurse/doctor if possible
        # If attending doctor not explicitly provided, derive based on requester role
        if not attending_doctor:
            req_role = getattr(user, 'role', None)
            if req_role == 'doctor':
                attending_doctor = getattr(user, 'doctor_profile', None)
        try:
            primary_nurse = patient.patient_profile.assigned_nurse if hasattr(patient, 'patient_profile') else None
        except Exception:
            primary_nurse = None
        # If requester is a nurse and no assigned nurse, use their profile
        if not primary_nurse and getattr(user, 'role', None) == 'nurse':
            primary_nurse = getattr(user, 'nurse_profile', None)

        # RBAC: patients can only request their own
        if getattr(user, 'role', None) == 'patient' and patient.id != user.id:
            return Response({'error': 'Patients can only request their own records.'}, status=status.HTTP_403_FORBIDDEN)

        mreq = MedicalRecordRequest.objects.create(
            patient=patient,
            requested_by=user,
            primary_nurse=primary_nurse,
            attending_doctor=attending_doctor,
            request_type=data.get('request_type') or '',
            requested_records=data.get('requested_records') or {},
            reason=data.get('reason') or '',
            urgency=data.get('urgency') or 'medium',
            purpose=data.get('purpose') or '',
            requested_date_range_start=data.get('requested_date_range_start'),
            requested_date_range_end=data.get('requested_date_range_end'),
            status='pending'
        )

        ArchiveAccessLog.objects.create(
            record=None, user=user, action='create', ip_address=request.META.get('REMOTE_ADDR', ''), query_params=str(request.data)
        )

        # Notify doctor and nurse, and the patient
        notif = {
            'type': 'medical_record_request',
            'request_id': mreq.id,
            'patient_id': patient.id,
            'patient_name': getattr(patient, 'full_name', patient.email),
            'requested_by': getattr(user, 'full_name', user.email),
            'urgency': mreq.urgency,
            'reason': mreq.reason,
            'status': mreq.status,
        }
        targets = [getattr(getattr(mreq.attending_doctor, 'user', None), 'id', None),
                   getattr(getattr(mreq.primary_nurse, 'user', None), 'id', None),
                   patient.id]
        _broadcast_notification(targets, notif)

        return Response(MedicalRecordRequestSerializer(mreq).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_medical_request(request, request_id: int):
    user: User = request.user
    role = getattr(user, 'role', None)
    if role != 'doctor':
        return Response({'error': 'Only doctors can approve record requests.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        mreq = MedicalRecordRequest.objects.get(id=request_id)
    except MedicalRecordRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        mreq.status = 'approved'
        mreq.approved_by = user
        mreq.approved_at = timezone.now()
        mreq.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])

        ArchiveAccessLog.objects.create(
            record=None, user=user, action='update', ip_address=request.META.get('REMOTE_ADDR', ''), query_params=f'approve:{mreq.id}'
        )

        notif = {
            'type': 'medical_record_request_approved',
            'request_id': mreq.id,
            'patient_id': mreq.patient_id,
            'approved_by': getattr(user, 'full_name', user.email)
        }
        targets = [mreq.patient_id, getattr(getattr(mreq.primary_nurse, 'user', None), 'id', None)]
        _broadcast_notification(targets, notif)

    serializer = MedicalRecordRequestSerializer(mreq, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deliver_medical_request(request, request_id: int):
    user: User = request.user
    role = getattr(user, 'role', None)
    if role != 'doctor':
        return Response({'error': 'Only doctors can deliver medical records.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        mreq = MedicalRecordRequest.objects.get(id=request_id)
    except MedicalRecordRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    if mreq.status not in ['approved', 'pending']:
        return Response({'error': f'Cannot deliver in current status: {mreq.status}'}, status=status.HTTP_400_BAD_REQUEST)

    # Optional: enforce approved first
    if mreq.status == 'pending':
        return Response({'error': 'Request must be approved before delivery.'}, status=status.HTTP_400_BAD_REQUEST)

    # Gather records and generate + encrypt PDF
    patient = mreq.patient
    doctor_user = user
    records_payload = _collect_records(patient, mreq.requested_records)

    pdf_bytes = generate_records_pdf(
        patient_name=getattr(patient, 'full_name', patient.email),
        patient_email=getattr(patient, 'email', ''),
        details={
            'request': {
                'id': mreq.id,
                'type': mreq.request_type,
                'urgency': mreq.urgency,
                'reason': mreq.reason,
                'approved_at': str(mreq.approved_at) if mreq.approved_at else None,
            },
            'records': records_payload
        }
    )
    password = _build_password(doctor_user, patient)
    encrypted_bytes = encrypt_pdf_aes256(pdf_bytes, password)

    filename = f"medical-records-{patient.id}-{mreq.id}.pdf"
    send_encrypted_pdf_to_patient(getattr(patient, 'email', ''), encrypted_bytes, filename)

    with transaction.atomic():
        mreq.status = 'delivered'
        mreq.delivered_at = timezone.now()
        mreq.delivery_reference = filename
        mreq.save(update_fields=['status', 'delivered_at', 'delivery_reference', 'updated_at'])

        ArchiveAccessLog.objects.create(
            record=None, user=user, action='export', ip_address=request.META.get('REMOTE_ADDR', ''), query_params=f'deliver:{mreq.id}'
        )

    notif = {
        'type': 'medical_record_request_delivered',
        'request_id': mreq.id,
        'patient_id': mreq.patient_id,
        'delivery_reference': mreq.delivery_reference,
    }
    _broadcast_notification([mreq.patient_id], notif)

    serializer = MedicalRecordRequestSerializer(mreq, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_medical_request(request, request_id: int):
    """Reject a medical certificate request."""
    user: User = request.user
    role = getattr(user, 'role', None)
    if role != 'doctor':
        return Response({'error': 'Only doctors can reject record requests.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        mreq = MedicalRecordRequest.objects.get(id=request_id)
    except MedicalRecordRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    rejection_reason = request.data.get('rejection_reason', '')
    if not rejection_reason:
        return Response({'error': 'Rejection reason is required.'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        mreq.status = 'rejected'
        mreq.rejected_by = user
        mreq.rejected_at = timezone.now()
        mreq.rejection_reason = rejection_reason
        mreq.save(update_fields=['status', 'rejected_by', 'rejected_at', 'rejection_reason', 'updated_at'])

        ArchiveAccessLog.objects.create(
            record=None, user=user, action='update', ip_address=request.META.get('REMOTE_ADDR', ''), 
            query_params=f'reject:{mreq.id}'
        )

        notif = {
            'type': 'medical_record_request_rejected',
            'request_id': mreq.id,
            'patient_id': mreq.patient_id,
            'rejected_by': getattr(user, 'full_name', user.email),
            'rejection_reason': rejection_reason,
        }
        targets = [mreq.patient_id, getattr(getattr(mreq.primary_nurse, 'user', None), 'id', None)]
        _broadcast_notification(targets, notif)

    serializer = MedicalRecordRequestSerializer(mreq, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_certificate(request, request_id: int):
    """Upload a medical certificate file for a request."""
    user: User = request.user
    role = getattr(user, 'role', None)
    if role != 'doctor':
        return Response({'error': 'Only doctors can upload certificates.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        mreq = MedicalRecordRequest.objects.get(id=request_id)
    except MedicalRecordRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    if 'certificate_file' not in request.FILES:
        return Response({'error': 'Certificate file is required.'}, status=status.HTTP_400_BAD_REQUEST)

    certificate_file = request.FILES['certificate_file']
    
    # Validate file type (PDF, images)
    allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    file_ext = certificate_file.name.lower().split('.')[-1] if '.' in certificate_file.name else ''
    if f'.{file_ext}' not in allowed_extensions:
        return Response({'error': 'Invalid file type. Allowed: PDF, PNG, JPG, JPEG'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        mreq.certificate_file = certificate_file
        if mreq.status == 'approved':
            mreq.status = 'completed'
        elif mreq.status == 'pending':
            mreq.status = 'processing'
        mreq.save(update_fields=['certificate_file', 'status', 'updated_at'])

        ArchiveAccessLog.objects.create(
            record=None, user=user, action='update', ip_address=request.META.get('REMOTE_ADDR', ''), 
            query_params=f'upload_certificate:{mreq.id}'
        )

        notif = {
            'type': 'medical_certificate_uploaded',
            'request_id': mreq.id,
            'patient_id': mreq.patient_id,
            'uploaded_by': getattr(user, 'full_name', user.email),
        }
        _broadcast_notification([mreq.patient_id], notif)

    serializer = MedicalRecordRequestSerializer(mreq, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_doctor_notes(request, request_id: int):
    """Add or update doctor notes for a medical certificate request."""
    user: User = request.user
    role = getattr(user, 'role', None)
    if role != 'doctor':
        return Response({'error': 'Only doctors can add notes.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        mreq = MedicalRecordRequest.objects.get(id=request_id)
    except MedicalRecordRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    doctor_notes = request.data.get('doctor_notes', '')
    
    with transaction.atomic():
        mreq.doctor_notes = doctor_notes
        if mreq.status == 'pending':
            mreq.status = 'processing'
        mreq.save(update_fields=['doctor_notes', 'status', 'updated_at'])

        ArchiveAccessLog.objects.create(
            record=None, user=user, action='update', ip_address=request.META.get('REMOTE_ADDR', ''), 
            query_params=f'add_notes:{mreq.id}'
        )

    serializer = MedicalRecordRequestSerializer(mreq, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_request_processing(request, request_id: int):
    """Mark a request as processing."""
    user: User = request.user
    role = getattr(user, 'role', None)
    if role != 'doctor':
        return Response({'error': 'Only doctors can mark requests as processing.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        mreq = MedicalRecordRequest.objects.get(id=request_id)
    except MedicalRecordRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    if mreq.status != 'pending':
        return Response({'error': f'Cannot mark as processing. Current status: {mreq.status}'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        mreq.status = 'processing'
        mreq.save(update_fields=['status', 'updated_at'])

        ArchiveAccessLog.objects.create(
            record=None, user=user, action='update', ip_address=request.META.get('REMOTE_ADDR', ''), 
            query_params=f'mark_processing:{mreq.id}'
        )

    serializer = MedicalRecordRequestSerializer(mreq, context={'request': request})
    return Response(serializer.data)