from django.db import transaction
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import datetime, date
from decimal import Decimal
import pyotp
import qrcode
import io
import base64

from .models import User, GeneralDoctorProfile, NurseProfile, PatientProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, VerificationDocumentSerializer, 
    ProfileUpdateSerializer, TwoFactorEnableSerializer,
    TwoFactorVerifySerializer, TwoFactorDisableSerializer, TwoFactorLoginSerializer
)

# These classes are correctly defined and can be used as they are.
# They are included here for the sake of a complete, organized file.
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token obtain pair serializer to include user data in the response.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user'] = UserSerializer(user).data
        return token
    
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view.
    """
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Registers a new user and creates their associated profile.
    This single endpoint handles all user roles (doctor, nurse, patient).
    The serializer handles all validation logic.
    """
    print("Received data:", request.data)  # Add debug logging
    serializer = UserRegistrationSerializer(data=request.data)
    print("Serializer is valid:", serializer.is_valid())  # Add debug logging
    if serializer.is_valid():
        try:
            with transaction.atomic():
                print("Creating user...")  # Add debug logging
                # Create the user from validated data
                user = serializer.save()
                print("User created successfully:", user.email)  # Add debug logging
                
                # Create the appropriate profile based on the user's role
                if user.role == 'doctor':
                    print("Creating doctor profile...")  # Add debug logging
                    GeneralDoctorProfile.objects.create(
                        user=user,
                        license_number=request.data.get('license_number'),
                        specialization=request.data.get('specialization')
                    )
                    print("Doctor profile created successfully")  # Add debug logging
                elif user.role == 'nurse':
                    NurseProfile.objects.create(
                        user=user,
                        license_number=request.data.get('license_number'),
                        department=request.data.get('department')
                    )
                elif user.role == 'patient':
                    PatientProfile.objects.create(
                        user=user,
                        blood_type=request.data.get('blood_type', PatientProfile.BloodType.UNKNOWN),
                        medical_condition=request.data.get('medical_condition', ''),
                        medication=request.data.get('medication', '')
                    )
                
                # Verify write persisted by querying freshly
                if not User.objects.filter(pk=user.pk).exists():
                    raise Exception("User record was not persisted to the database.")
                
                # Generate JWT tokens for the new user
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'User registered successfully',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            print("Exception occurred:", str(e))  # Add debug logging
            print("Exception type:", type(e))  # Add debug logging
            return Response({
                'error': 'Registration failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Return validation errors if data is invalid
    print("Validation errors:", serializer.errors)  # Add debug logging
    print("Error details:", dict(serializer.errors))  # Add more detailed logging
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Logs in a user with email and password and returns JWT tokens.
    If 2FA is enabled, requires OTP verification before returning tokens.
    """
    print("Login attempt - Email:", request.data.get('email'))  # Add debug logging
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Email and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    user = authenticate(request, email=email, password=password)
    print("Authentication result - User:", user)  # Add debug logging
    
    if user is not None:
        if not user.is_active:
            return Response({'error': 'User is not active.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if 2FA is enabled for this user
        if user.two_factor_enabled:
            # User has 2FA enabled, require OTP verification
            # Don't return tokens yet, return a flag indicating 2FA is required
            print("2FA enabled for user, requiring OTP verification")
            return Response({
                'requires_2fa': True,
                'email': user.email,
                'message': 'Please enter your 6-digit authentication code.'
            }, status=status.HTTP_200_OK)
        
        # No 2FA, proceed with normal login
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Use full serializer data to keep response consistent with /users/profile/
        user_data = UserSerializer(user).data
        print("User data from serializer:", user_data)  # Add debug logging
        
        response_data = {
            'message': 'Login successful',
            'user': user_data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        print("Login response data:", response_data)  # Add debug logging
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        print("Authentication failed - Invalid credentials")  # Add debug logging
        return Response({
            'error': 'Invalid credentials.',
            'message': 'Email or password is incorrect. Please try again.'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_verification_document(request):
    """
    Upload verification document for user identity verification
    """
    user = request.user
    serializer = VerificationDocumentSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        # Set verification status to pending when document is uploaded
        user.verification_status = 'pending'
        serializer.save()
        return Response({
            'message': 'Verification document uploaded successfully. Kindly wait for the admin to verify the uploaded file.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_now(request):
    """
    Submit verification request for admin review
    """
    user = request.user
    
    # Check if user already has a verification document
    if not user.verification_document:
        return Response({
            'error': 'Please upload a verification document first.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if verification request already exists
    from admin_site.models import VerificationRequest
    existing_request = VerificationRequest.objects.filter(
        user_email=user.email,
        status__in=['pending', 'approved']
    ).first()
    
    if existing_request:
        return Response({
            'error': 'Verification request already exists and is being processed.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create verification request
    verification_request = VerificationRequest.objects.create(
        user_email=user.email,
        user_full_name=user.full_name,
        user_role=user.role,
        verification_document=user.verification_document,
        status='pending'
    )
    
    # Update user verification status to pending
    user.verification_status = 'pending'
    user.save()
    
    return Response({
        'message': 'Verification request submitted successfully. Kindly wait for the admin to verify the uploaded file.',
        'user': UserSerializer(user).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get current user's profile information
    """
    return Response({
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)

# Deprecated: Removed endpoint for updating profile pictures


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update user's profile information including hospital details
    """
    serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Send password reset email to user
    """
    email = request.data.get('email')
    
    if not email:
        return Response({
            'error': 'Email is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        if not user.is_active:
            return Response({
                'error': 'User account is not active.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Create reset URL (for now, we'll use a simple approach)
        reset_url = f"http://localhost:9000/#/reset-password/{uid}/{token}"
        
        # Send password reset email
        subject = 'Password Reset Request - MediSync'
        message = f"""
        Hello {user.full_name},
        
        You have requested to reset your password for your MediSync account.
        
        Please click the following link to reset your password:
        {reset_url}
        
        If you did not request this password reset, please ignore this email.
        
        This link will expire in 24 hours.
        
        Best regards,
        MediSync Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # From email
                [user.email],  # To email
                fail_silently=False,
            )
            
            return Response({
                'message': 'Password reset link has been sent to your email.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return Response({
                'error': 'Failed to send password reset email. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except User.DoesNotExist:
        # Don't reveal if email exists or not for security
        return Response({
            'message': 'If an account with this email exists, a password reset link has been sent.'
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, uidb64, token):
    """
    Reset user password using token
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response({
                'error': 'New password is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password
        if len(new_password) < 8:
            return Response({
                'error': 'Password must be at least 8 characters long.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if password contains alphanumeric characters
        if not any(c.isalpha() for c in new_password) or not any(c.isdigit() for c in new_password):
            return Response({
                'error': 'Password must contain both letters and numbers.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password has been reset successfully.'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Invalid or expired reset link.'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_patients(request):
    """
    Get all patients for a doctor with optional search functionality (including dummy data for analytics)
    """
    if request.user.role != 'doctor':
        return Response({
            'error': 'Only doctors can access this endpoint.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get search parameter
        search_query = request.GET.get('search', '').strip()
        
        # Get all patients (including dummy data)
        patients = PatientProfile.objects.select_related('user').all()
        
        # Apply search filter if search query is provided
        if search_query:
            patients = patients.filter(
                Q(user__full_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(medical_condition__icontains=search_query) |
                Q(blood_type__icontains=search_query) |
                Q(hospital__icontains=search_query) |
                Q(insurance_provider__icontains=search_query) |
                Q(room_number__icontains=search_query) |
                Q(medication__icontains=search_query)
            )
        
        # Serialize patient data
        patient_data = []
        for patient in patients:
            patient_info = {
                'id': patient.id,
                'user_id': patient.user.id,
                'full_name': patient.user.full_name,
                'email': patient.user.email,
                'age': calculate_age(patient.user.date_of_birth) if patient.user.date_of_birth else None,
                'gender': patient.user.gender,
                'blood_type': patient.blood_type,
                'medical_condition': patient.medical_condition,
                'hospital': patient.hospital,
                'insurance_provider': patient.insurance_provider,
                'billing_amount': float(patient.billing_amount) if patient.billing_amount else None,
                'room_number': patient.room_number,
                'admission_type': patient.admission_type,
                'date_of_admission': patient.date_of_admission,
                'discharge_date': patient.discharge_date,
                'medication': patient.medication,
                'test_results': patient.test_results,
                'is_dummy': 'dummy' in patient.user.email,
                'assigned_doctor': patient.assigned_doctor.full_name if patient.assigned_doctor else None
            }
            patient_data.append(patient_info)
        
        return Response({
            'success': True,
            'patients': patient_data,
            'total_count': len(patient_data),
            'dummy_count': len([p for p in patient_data if p['is_dummy']]),
            'real_count': len([p for p in patient_data if not p['is_dummy']])
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error fetching patients: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_nurse_patients(request):
    """
    Get all patients for a nurse with optional search functionality (including dummy data for analytics)
    """
    if request.user.role != 'nurse':
        return Response({
            'error': 'Only nurses can access this endpoint.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get search parameter
        search_query = request.GET.get('search', '').strip()
        
        # Get all patients (including dummy data)
        patients = PatientProfile.objects.select_related('user').all()
        
        # Apply search filter if search query is provided
        if search_query:
            patients = patients.filter(
                Q(user__full_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(medical_condition__icontains=search_query) |
                Q(blood_type__icontains=search_query) |
                Q(hospital__icontains=search_query) |
                Q(insurance_provider__icontains=search_query) |
                Q(room_number__icontains=search_query) |
                Q(medication__icontains=search_query)
            )
        
        # Serialize patient data
        patient_data = []
        for patient in patients:
            patient_info = {
                'id': patient.id,
                'user_id': patient.user.id,
                'full_name': patient.user.full_name,
                'email': patient.user.email,
                'age': calculate_age(patient.user.date_of_birth) if patient.user.date_of_birth else None,
                'gender': patient.user.gender,
                'blood_type': patient.blood_type,
                'medical_condition': patient.medical_condition,
                'hospital': patient.hospital,
                'insurance_provider': patient.insurance_provider,
                'billing_amount': float(patient.billing_amount) if patient.billing_amount else None,
                'room_number': patient.room_number,
                'admission_type': patient.admission_type,
                'date_of_admission': patient.date_of_admission,
                'discharge_date': patient.discharge_date,
                'medication': patient.medication,
                'test_results': patient.test_results,
                'is_dummy': 'dummy' in patient.user.email,
                'assigned_doctor': patient.assigned_doctor.full_name if patient.assigned_doctor else None
            }
            patient_data.append(patient_info)
        
        return Response({
            'success': True,
            'patients': patient_data,
            'total_count': len(patient_data),
            'dummy_count': len([p for p in patient_data if p['is_dummy']]),
            'real_count': len([p for p in patient_data if not p['is_dummy']])
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error fetching patients: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


# ============================================
# Two-Factor Authentication (2FA) Endpoints
# ============================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """
    Initiate 2FA setup for doctors and nurses only.
    Generates a secret key and returns a QR code for scanning with an authenticator app.
    """
    user = request.user
    
    # Only allow doctors and nurses to enable 2FA
    if user.role not in ['doctor', 'nurse']:
        return Response({
            'error': 'Two-factor authentication is only available for doctors and nurses.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Check if 2FA is already enabled
    if user.two_factor_enabled:
        return Response({
            'error': 'Two-factor authentication is already enabled for this account.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate a new secret key
    secret = pyotp.random_base32()
    
    # Save the secret temporarily (it will be finalized upon verification)
    user.two_factor_secret = secret
    user.save()
    
    # Generate provisioning URI for QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name='MediSync'
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64 for easy transmission
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return Response({
        'message': 'Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)',
        'qr_code': f'data:image/png;base64,{qr_code_base64}',
        'secret': secret,  # Also provide secret for manual entry
        'next_step': 'Enter the 6-digit code from your authenticator app to verify and activate 2FA'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    """
    Verify and activate 2FA by checking the OTP code from authenticator app.
    """
    user = request.user
    serializer = TwoFactorVerifySerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if 2FA is already enabled
    if user.two_factor_enabled:
        return Response({
            'error': 'Two-factor authentication is already enabled for this account.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if secret exists
    if not user.two_factor_secret:
        return Response({
            'error': 'No 2FA setup found. Please initiate 2FA setup first.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    otp_code = serializer.validated_data['otp_code']
    
    # Verify the OTP code
    totp = pyotp.TOTP(user.two_factor_secret)
    if totp.verify(otp_code, valid_window=1):
        # OTP is valid, enable 2FA
        user.two_factor_enabled = True
        user.save()
        
        return Response({
            'message': 'Two-factor authentication has been successfully enabled for your account.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Invalid authentication code. Please try again.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """
    Disable 2FA for the user after password verification.
    """
    user = request.user
    serializer = TwoFactorDisableSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if 2FA is enabled
    if not user.two_factor_enabled:
        return Response({
            'error': 'Two-factor authentication is not enabled for this account.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify password
    password = serializer.validated_data['password']
    if not user.check_password(password):
        return Response({
            'error': 'Invalid password. Please try again.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Disable 2FA
    user.two_factor_enabled = False
    user.two_factor_secret = None
    user.save()
    
    return Response({
        'message': 'Two-factor authentication has been successfully disabled for your account.',
        'user': UserSerializer(user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_2fa_login(request):
    """
    Verify OTP code during login for users with 2FA enabled.
    Returns JWT tokens if OTP is valid.
    """
    serializer = TwoFactorLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp_code']
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid credentials.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user is active
    if not user.is_active:
        return Response({
            'error': 'User account is not active.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if 2FA is enabled
    if not user.two_factor_enabled or not user.two_factor_secret:
        return Response({
            'error': 'Two-factor authentication is not enabled for this account.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify the OTP code
    totp = pyotp.TOTP(user.two_factor_secret)
    if totp.verify(otp_code, valid_window=1):
        # OTP is valid, generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Use full serializer data to keep response consistent with /users/profile/
        user_data = UserSerializer(user).data
        
        return Response({
            'message': 'Login successful',
            'user': user_data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Invalid authentication code. Please try again.'
        }, status=status.HTTP_400_BAD_REQUEST)
