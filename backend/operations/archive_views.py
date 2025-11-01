from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime
from django.core.cache import cache
from django.db import transaction
import os

from backend.users.models import User, GeneralDoctorProfile
from .models import PatientAssessmentArchive, ArchiveAccessLog
from .serializers import PatientAssessmentArchiveSerializer, ArchiveAccessLogSerializer

import hmac
import hashlib
import json
from django.conf import settings

# --- Dual-store helpers ---
DUAL_STORE_ROOT = os.path.join(os.path.dirname(__file__), 'dual_store')
DOCTOR_STORE_DIR = os.path.join(DUAL_STORE_ROOT, 'doctor_archives')
NURSE_STORE_DIR = os.path.join(DUAL_STORE_ROOT, 'nurse_archives')

def _ensure_dual_store_dirs():
    try:
        os.makedirs(DOCTOR_STORE_DIR, exist_ok=True)
        os.makedirs(NURSE_STORE_DIR, exist_ok=True)
    except Exception:
        # Directory creation failure will be handled by caller
        pass

def _dual_store_write(record_id: int, payload: dict):
    """Write identical JSON payload to doctor and nurse archive files.
    Returns tuple (doctor_path, nurse_path). Raises on failure and attempts cleanup.
    """
    _ensure_dual_store_dirs()
    doc_path = os.path.join(DOCTOR_STORE_DIR, f"archive_{record_id}.json")
    nur_path = os.path.join(NURSE_STORE_DIR, f"archive_{record_id}.json")
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    wrote_doc = False
    wrote_nur = False
    try:
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(serialized)
        wrote_doc = True
        with open(nur_path, 'w', encoding='utf-8') as f:
            f.write(serialized)
        wrote_nur = True
        return doc_path, nur_path
    except Exception as e:
        # Attempt cleanup if one file was written
        try:
            if wrote_doc and os.path.exists(doc_path):
                os.remove(doc_path)
        except Exception:
            pass
        try:
            if wrote_nur and os.path.exists(nur_path):
                os.remove(nur_path)
        except Exception:
            pass
        raise e

def _record_payload_for_dual_store(record: PatientAssessmentArchive) -> dict:
    return {
        'id': record.id,
        'patient_id': getattr(record.user, 'id', None),
        'patient_name': getattr(record.user, 'full_name', ''),
        'assessment_type': record.assessment_type,
        'medical_condition': record.medical_condition,
        'medical_history_summary': record.medical_history_summary,
        'diagnostics': record.diagnostics,
        'last_assessed_at': record.last_assessed_at.isoformat() if record.last_assessed_at else None,
        'hospital_name': record.hospital_name,
        'assessment': record.decrypt_payload(),
    }

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def archive_list(request):
    """List archived patient assessments with search and filters"""
    start_time = timezone.now()
    try:
        qs = PatientAssessmentArchive.objects.filter(assessment_data__archived=True)
        patient_id = request.GET.get('patient_id')
        patient_name = request.GET.get('patient_name')
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        assessment_type = request.GET.get('assessment_type')
        condition = request.GET.get('condition')

        if patient_id:
            qs = qs.filter(user__id=patient_id)
        if patient_name:
            qs = qs.filter(user__full_name__icontains=patient_name)
        if assessment_type:
            qs = qs.filter(assessment_type__iexact=assessment_type)
        if condition:
            qs = qs.filter(medical_condition__icontains=condition)
        if start_date:
            try:
                sd = datetime.strptime(start_date, '%Y-%m-%d').date()
                qs = qs.filter(last_assessed_at__date__gte=sd)
            except Exception:
                pass
        if end_date:
            try:
                ed = datetime.strptime(end_date, '%Y-%m-%d').date()
                qs = qs.filter(last_assessed_at__date__lte=ed)
            except Exception:
                pass

        cache_key = f"archives:list:{request.user.id}:{hash(frozenset(request.GET.items()))}"
        cached = cache.get(cache_key)
        if cached:
            try:
                ArchiveAccessLog.objects.create(
                    user=request.user, action='search', record=qs.first() if qs.exists() else None,
                    query_params=str(dict(request.GET)), duration_ms=int((timezone.now()-start_time).total_seconds()*1000)
                )
            except Exception:
                pass
            return Response(cached, status=status.HTTP_200_OK)

        serializer = PatientAssessmentArchiveSerializer(qs.order_by('-last_assessed_at')[:200], many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)

        try:
            ArchiveAccessLog.objects.create(
                user=request.user, action='search', record=qs.first() if qs.exists() else None,
                query_params=str(dict(request.GET)), duration_ms=int((timezone.now()-start_time).total_seconds()*1000)
            )
        except Exception:
            pass
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Failed to list archives: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def archive_detail(request, archive_id):
    """Get a single archived assessment (decrypted)"""
    start_time = timezone.now()
    try:
        record = PatientAssessmentArchive.objects.filter(id=archive_id).first()
        if not record:
            return Response({'error': 'Archive record not found'}, status=status.HTTP_404_NOT_FOUND)

        cache_key = f"archives:detail:{archive_id}"
        cached = cache.get(cache_key)
        if cached:
            ArchiveAccessLog.objects.create(
                user=request.user, action='view', record=record,
                duration_ms=int((timezone.now()-start_time).total_seconds()*1000),
            )
            return Response(cached, status=status.HTTP_200_OK)

        serializer = PatientAssessmentArchiveSerializer(record)
        data = serializer.data
        cache.set(cache_key, data, timeout=120)

        ArchiveAccessLog.objects.create(
            user=request.user, action='view', record=record,
            duration_ms=int((timezone.now()-start_time).total_seconds()*1000),
        )
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Failed to fetch archive: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _verify_signature(payload: dict, signature: str) -> bool:
    """Verify HMAC-SHA256 signature of the payload using TRANSMISSION_SIGNING_KEY.
    When key is absent, treat verification as optional (development mode)."""
    secret = getattr(settings, 'TRANSMISSION_SIGNING_KEY', None)
    if not secret:
        return True  # skip verification in dev if key not configured
    if isinstance(secret, str):
        secret = secret.encode()
    raw = json.dumps(payload or {}, sort_keys=True, ensure_ascii=False).encode()
    expected = hmac.new(secret, raw, hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(expected, signature or '')
    except Exception:
        return False


def _doctor_specialization_is_valid(doctor_id: int, specialization: str) -> bool:
    doc = GeneralDoctorProfile.objects.filter(user__id=doctor_id, user__verification_status='approved').first()
    if not doc:
        return False
    if not specialization:
        return False
    return specialization.lower() in (doc.specialization or '').lower()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def archive_create(request):
    """Create a new archived assessment record with optional signature and specialization verification."""
    start_time = timezone.now()
    try:
        payload = request.data or {}
        patient_id = payload.get('patient_id')
        doctor_id = payload.get('doctor_id')
        specialization = payload.get('specialization')
        signature = payload.get('signature')
        assessment_type_val = payload.get('assessment_type', '').strip()
        assessment_data_val = payload.get('assessment_data') or {}
        if isinstance(assessment_data_val, str):
            try:
                assessment_data_val = json.loads(assessment_data_val)
            except Exception:
                return Response({'error': 'assessment_data must be valid JSON', 'code': 'ERR_BAD_ASSESSMENT_DATA'}, status=status.HTTP_400_BAD_REQUEST)

        if not patient_id:
            return Response({'error': 'patient_id is required', 'code': 'ERR_MISSING_PATIENT'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(id=patient_id).first()
        if not user:
            return Response({'error': 'Patient not found', 'code': 'ERR_PATIENT_NOT_FOUND'}, status=status.HTTP_404_NOT_FOUND)

        # Basic validation
        if not assessment_type_val:
            return Response({'error': 'assessment_type is required', 'code': 'ERR_MISSING_TYPE'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(assessment_data_val, dict) or not assessment_data_val:
            return Response({'error': 'assessment_data is required', 'code': 'ERR_MISSING_DATA'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify specialization/doctor if provided
        if doctor_id or specialization:
            if not (doctor_id and specialization):
                ArchiveAccessLog.objects.create(user=request.user, action='create', record=None, query_params=json.dumps({'doctor_id': doctor_id, 'specialization': specialization, 'status': 'failure', 'code': 'ERR_MISSING_DOCTOR_SPECIALIZATION'}))
                return Response({'error': 'Doctor ID and specialization are required', 'code': 'ERR_MISSING_DOCTOR_SPECIALIZATION'}, status=status.HTTP_400_BAD_REQUEST)
            if not _doctor_specialization_is_valid(int(doctor_id), str(specialization)):
                ArchiveAccessLog.objects.create(user=request.user, action='create', record=None, query_params=json.dumps({'doctor_id': doctor_id, 'specialization': specialization, 'status': 'failure', 'code': 'ERR_SPECIALIZATION_MISMATCH'}))
                return Response({'error': 'Doctor verification/specialization mismatch', 'code': 'ERR_SPECIALIZATION_MISMATCH'}, status=status.HTTP_403_FORBIDDEN)

        # Verify digital signature if provided
        if signature and not _verify_signature(assessment_data_val, signature):
            ArchiveAccessLog.objects.create(user=request.user, action='create', record=None, query_params=json.dumps({'doctor_id': doctor_id, 'specialization': specialization, 'status': 'failure', 'code': 'ERR_BAD_SIGNATURE'}))
            return Response({'error': 'Bad digital signature', 'code': 'ERR_BAD_SIGNATURE'}, status=status.HTTP_401_UNAUTHORIZED)
        # Mark as archived in assessment_data
        assessment_data_val['archived'] = True

        # Transactional create with dual store write
        with transaction.atomic():
            record = PatientAssessmentArchive.objects.create(
                user=user,
                assessment_type=assessment_type_val,
                medical_condition=payload.get('medical_condition', ''),
                medical_history_summary=payload.get('medical_history_summary', ''),
                diagnostics=payload.get('diagnostics') or {},
                assessment_data=assessment_data_val,
                last_assessed_at=payload.get('last_assessed_at') or timezone.now(),
                hospital_name=payload.get('hospital_name', ''),
            )
            # Write to dual store; throw to trigger rollback if failed
            _dual_store_write(record.id, _record_payload_for_dual_store(record))
        serializer = PatientAssessmentArchiveSerializer(record)
        ArchiveAccessLog.objects.create(
            user=request.user,
            action='create',
            record=record,
            query_params=json.dumps({'doctor_id': doctor_id, 'specialization': specialization, 'status': 'success'}),
            duration_ms=int((timezone.now()-start_time).total_seconds()*1000)
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        ArchiveAccessLog.objects.create(user=request.user, action='create', record=None, query_params=json.dumps({'status': 'failure', 'code': 'ERR_SERVER', 'message': str(e)}))
        return Response({'error': f'Failed to create archive: {str(e)}', 'code': 'ERR_SERVER'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def archive_export(request, archive_id):
    """Export a single archived assessment as standardized JSON"""
    start_time = timezone.now()
    try:
        record = PatientAssessmentArchive.objects.filter(id=archive_id).first()
        if not record:
            return Response({'error': 'Archive record not found'}, status=status.HTTP_404_NOT_FOUND)

        cache_key = f"archives:export:{archive_id}"
        cached = cache.get(cache_key)
        if cached:
            ArchiveAccessLog.objects.create(
                user=request.user, action='export', record=record,
                duration_ms=int((timezone.now()-start_time).total_seconds()*1000),
            )
            return Response(cached, status=status.HTTP_200_OK, headers={
                'Content-Disposition': f'attachment; filename="archive_{archive_id}.json"'
            })

        payload = {
            'id': record.id,
            'patient_id': record.user.id,
            'patient_name': record.user.full_name,
            'assessment_type': record.assessment_type,
            'medical_condition': record.medical_condition,
            'medical_history_summary': record.medical_history_summary,
            'diagnostics': record.diagnostics,
            'last_assessed_at': record.last_assessed_at.isoformat() if record.last_assessed_at else None,
            'hospital_name': record.hospital_name,
            'assessment': record.decrypt_payload(),
        }
        cache.set(cache_key, payload, timeout=180)

        ArchiveAccessLog.objects.create(
            user=request.user, action='export', record=record,
            duration_ms=int((timezone.now()-start_time).total_seconds()*1000),
        )
        return Response(payload, status=status.HTTP_200_OK, headers={
            'Content-Disposition': f'attachment; filename="archive_{archive_id}.json"'
        })
    except Exception as e:
        return Response({'error': f'Failed to export archive: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def archive_logs(request):
    """Return archive access logs filtered by doctor_id, patient_id, or record_id for audit trails."""
    try:
        doctor_id = request.GET.get('doctor_id')
        patient_id = request.GET.get('patient_id')
        record_id = request.GET.get('record_id')
        limit = int(request.GET.get('limit') or 200)

        logs = ArchiveAccessLog.objects.all()
        if record_id:
            logs = logs.filter(record__id=record_id)
        if patient_id:
            logs = logs.filter(record__user__id=patient_id)
        if doctor_id:
            logs = logs.filter(user__id=doctor_id)

        logs = logs.order_by('-accessed_at')[:limit]
        serializer = ArchiveAccessLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Failed to fetch archive logs: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def archive_update(request, archive_id):
    """Update an archived assessment and reflect changes to dual store files."""
    try:
        record = PatientAssessmentArchive.objects.filter(id=archive_id).first()
        if not record:
            return Response({'error': 'Archive record not found'}, status=status.HTTP_404_NOT_FOUND)

        payload = request.data or {}
        updated_fields = {}
        if 'assessment_type' in payload:
            updated_fields['assessment_type'] = str(payload.get('assessment_type') or '')
        if 'medical_condition' in payload:
            updated_fields['medical_condition'] = str(payload.get('medical_condition') or '')
        if 'medical_history_summary' in payload:
            updated_fields['medical_history_summary'] = str(payload.get('medical_history_summary') or '')
        if 'diagnostics' in payload:
            updated_fields['diagnostics'] = payload.get('diagnostics') or {}
        if 'assessment_data' in payload:
            assessment_data_val = payload.get('assessment_data')
            if isinstance(assessment_data_val, str):
                try:
                    assessment_data_val = json.loads(assessment_data_val)
                except Exception:
                    return Response({'error': 'assessment_data must be valid JSON', 'code': 'ERR_BAD_ASSESSMENT_DATA'}, status=status.HTTP_400_BAD_REQUEST)
            if not isinstance(assessment_data_val, dict):
                return Response({'error': 'assessment_data must be an object'}, status=status.HTTP_400_BAD_REQUEST)
            # Preserve archived flag unless caller sets it
            if 'archived' not in assessment_data_val:
                assessment_data_val['archived'] = True
            updated_fields['assessment_data'] = assessment_data_val

        with transaction.atomic():
            for k, v in updated_fields.items():
                setattr(record, k, v)
            record.save()
            _dual_store_write(record.id, _record_payload_for_dual_store(record))

        serializer = PatientAssessmentArchiveSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Failed to update archive: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def archive_unarchive(request, archive_id):
    """Mark an archive as unarchived (archived=false) and update dual files."""
    try:
        record = PatientAssessmentArchive.objects.filter(id=archive_id).first()
        if not record:
            return Response({'error': 'Archive record not found'}, status=status.HTTP_404_NOT_FOUND)
        data = record.assessment_data or {}
        if isinstance(data, dict):
            data['archived'] = False
        else:
            data = {'archived': False}

        with transaction.atomic():
            record.assessment_data = data
            record.save()
            _dual_store_write(record.id, _record_payload_for_dual_store(record))

        return Response({'success': True, 'message': 'Record unarchived', 'id': record.id}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Failed to unarchive: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)