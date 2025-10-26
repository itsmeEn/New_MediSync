from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import SecureKey, SecureTransmission, TransmissionAudit, MFAChallenge
from backend.users.models import PatientProfile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def register_public_key(request):
    public_key_pem = request.data.get('public_key_pem')
    algorithm = request.data.get('algorithm', 'RSA-OAEP-2048-SHA256')
    if not public_key_pem:
        return Response({'error': 'public_key_pem is required'}, status=status.HTTP_400_BAD_REQUEST)
    SecureKey.objects.filter(user=request.user, is_active=True).update(is_active=False)
    key = SecureKey.objects.create(user=request.user, public_key_pem=public_key_pem, algorithm=algorithm, is_active=True)
    TransmissionAudit.objects.create(transmission=None, event='key_registered', detail=f'algorithm={algorithm}', actor=request.user)
    return Response({'message': 'Public key registered', 'key_id': key.id}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_public_key(request, doctor_id):
    key = SecureKey.objects.filter(user_id=doctor_id, is_active=True).order_by('-created_at').first()
    if not key:
        return Response({'error': 'No active public key for doctor'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'doctor_id': doctor_id, 'public_key_pem': key.public_key_pem, 'algorithm': key.algorithm})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_secure_transmission(request):
    data = request.data
    required = ['receiver_id','patient_id','ciphertext_b64','iv_b64','encrypted_key_b64','signature_b64','signing_public_key_pem','checksum_hex']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return Response({'error': f'Missing fields: {", ".join(missing)}'}, status=status.HTTP_400_BAD_REQUEST)
    # Resolve patient by either profile id or user id to be robust
    try:
        pid = data.get('patient_id')
        patient = PatientProfile.objects.filter(id=pid).first() or PatientProfile.objects.filter(user_id=pid).first()
        if not patient:
            return Response({'error': 'Invalid patient_id'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({'error': 'Invalid patient_id'}, status=status.HTTP_400_BAD_REQUEST)

    transmission = SecureTransmission.objects.create(
        sender=request.user,
        receiver_id=data.get('receiver_id'),
        patient=patient,
        ciphertext_b64=data.get('ciphertext_b64'),
        iv_b64=data.get('iv_b64'),
        encrypted_key_b64=data.get('encrypted_key_b64'),
        signature_b64=data.get('signature_b64'),
        signing_public_key_pem=data.get('signing_public_key_pem'),
        checksum_hex=data.get('checksum_hex'),
        encryption_alg=data.get('encryption_alg', 'AES-256-GCM'),
        signature_alg=data.get('signature_alg', 'ECDSA-P256-SHA256'),
        status='pending'
    )
    TransmissionAudit.objects.create(transmission=transmission, event='created', detail='Secure transmission created', actor=request.user)
    return Response({'message': 'Transmission created', 'id': transmission.id}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_transmissions_for_doctor(request):
    qs = SecureTransmission.objects.filter(receiver=request.user).order_by('-created_at')
    status_filter = request.query_params.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)
    items = []
    for t in qs[:200]:
        items.append({
            'id': t.id,
            'sender_id': t.sender_id,
            'patient_id': t.patient_id,
            'created_at': t.created_at,
            'status': t.status,
            'encryption_alg': t.encryption_alg,
            'signature_alg': t.signature_alg
        })
    return Response({'items': items})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transmission_detail(request, transmission_id):
    try:
        t = SecureTransmission.objects.get(id=transmission_id, receiver=request.user)
    except SecureTransmission.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    payload = {
        'id': t.id,
        'ciphertext_b64': t.ciphertext_b64,
        'iv_b64': t.iv_b64,
        'encrypted_key_b64': t.encrypted_key_b64,
        'signature_b64': t.signature_b64,
        'signing_public_key_pem': t.signing_public_key_pem,
        'checksum_hex': t.checksum_hex,
        'encryption_alg': t.encryption_alg,
        'signature_alg': t.signature_alg,
        'created_at': t.created_at,
        'patient_id': t.patient_id,
        'sender_id': t.sender_id
    }
    return Response(payload)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def mark_transmission_accessed(request, transmission_id):
    try:
        t = SecureTransmission.objects.get(id=transmission_id, receiver=request.user)
    except SecureTransmission.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    t.status = 'received'
    t.accessed_at = timezone.now()
    t.save(update_fields=['status','accessed_at'])
    TransmissionAudit.objects.create(transmission=t, event='received', detail='Marked as received', actor=request.user)
    return Response({'message': 'Marked as received'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def mfa_challenge(request):
    import random
    code = f"{random.randint(0, 999999):06d}"
    expires = timezone.now() + timezone.timedelta(minutes=5)
    MFAChallenge.objects.filter(user=request.user, is_used=False).update(is_used=True)
    challenge = MFAChallenge.objects.create(user=request.user, code=code, expires_at=expires)
    TransmissionAudit.objects.create(transmission=None, event='mfa_challenge', detail=f'expires={expires.isoformat()}', actor=request.user)
    return Response({'challenge_id': challenge.id, 'expires_at': expires, 'code_dev_only': code})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def mfa_verify(request):
    code = request.data.get('code')
    if not code:
        return Response({'error': 'code is required'}, status=status.HTTP_400_BAD_REQUEST)
    now = timezone.now()
    challenge = MFAChallenge.objects.filter(user=request.user, is_used=False).order_by('-created_at').first()
    if not challenge:
        return Response({'error': 'No active challenge'}, status=status.HTTP_400_BAD_REQUEST)
    if challenge.code != code:
        TransmissionAudit.objects.create(transmission=None, event='mfa_failed', detail='Code mismatch', actor=request.user)
        return Response({'error': 'Invalid code'}, status=status.HTTP_401_UNAUTHORIZED)
    if challenge.expires_at < now:
        TransmissionAudit.objects.create(transmission=None, event='mfa_failed', detail='Code expired', actor=request.user)
        return Response({'error': 'Code expired'}, status=status.HTTP_401_UNAUTHORIZED)
    challenge.is_used = True
    challenge.save(update_fields=['is_used'])
    TransmissionAudit.objects.create(transmission=None, event='mfa_verified', detail='MFA verified', actor=request.user)
    return Response({'message': 'MFA verified'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def report_breach(request, transmission_id):
    try:
        t = SecureTransmission.objects.get(id=transmission_id)
    except SecureTransmission.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    t.breach_flag = True
    t.breach_notified_at = timezone.now()
    t.save(update_fields=['breach_flag','breach_notified_at'])
    TransmissionAudit.objects.create(transmission=t, event='breach_reported', detail='Breach notification filed', actor=request.user)
    return Response({'message': 'Breach reported'})