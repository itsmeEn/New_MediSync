from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import os

from .models import AdminUser, VerificationRequest, SystemLog
from .serializers import (
    AdminUserSerializer, AdminLoginSerializer, AdminRegistrationSerializer, VerificationRequestSerializer,
    VerificationRequestUpdateSerializer, DeclineVerificationSerializer, SystemLogSerializer
)
from .authentication import AdminJWTAuthentication


def log_admin_action(admin_user, action, target, target_id, details=""):
    """Helper function to log admin actions."""
    SystemLog.objects.create(
        admin_user=admin_user,
        action=action,
        target=target,
        target_id=target_id,
        details=details
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def admin_overview(request):
    """
    Admin API overview - provides information about available endpoints
    """
    return Response({
        'message': 'MediSync Admin API',
        'version': '1.0.0',
        'endpoints': {
            'login': '/api/admin/login/',
            'dashboard_stats': '/api/admin/dashboard/stats/',
            'verifications': '/api/admin/verifications/',
            'system_logs': '/api/admin/logs/',
        },
        'description': 'Administrative interface for managing user verifications and system operations'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """
    Get CSRF token for admin frontend
    """
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    return Response({
        'csrf_token': csrf_token
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """
    Admin login endpoint
    """
    serializer = AdminLoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Use the custom AdminUserBackend for authentication
        from .backends import AdminUserBackend
        backend = AdminUserBackend()
        user = backend.authenticate(request, email=email, password=password)
        
        if user and isinstance(user, AdminUser):
            if not user.is_active:
                return Response({
                    'error': 'Account is deactivated.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if email is verified
            if not user.is_email_verified:
                return Response({
                    'error': 'Email not verified.',
                    'message': 'Please verify your email address before logging in.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'admin_user': AdminUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials.',
                'message': 'Email or password is incorrect.'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_register(request):
    """
    Admin registration endpoint with email verification
    """
    serializer = AdminRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Create admin user
            admin_user = AdminUser.objects.create_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                full_name=serializer.validated_data['full_name'],
                is_super_admin=serializer.validated_data.get('is_super_admin', False)
            )
            
            # Generate email verification token
            from django.utils import timezone
            from django.utils.crypto import get_random_string
            import uuid
            
            verification_token = str(uuid.uuid4())
            admin_user.email_verification_token = verification_token
            admin_user.email_verification_sent_at = timezone.now()
            admin_user.save()
            
            # Send verification email
            send_verification_email(admin_user, verification_token)
            
            return Response({
                'message': 'Admin account created successfully. Please check your email for verification.',
                'admin_user': {
                    'id': admin_user.id,
                    'email': admin_user.email,
                    'full_name': admin_user.full_name,
                    'is_email_verified': admin_user.is_email_verified
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Failed to create admin account: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_admin_email(request):
    """
    Verify admin email with token
    """
    token = request.data.get('token')
    if not token:
        return Response({
            'error': 'Verification token is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        admin_user = AdminUser.objects.get(email_verification_token=token)
        
        # Check if token is expired (24 hours)
        from django.utils import timezone
        from datetime import timedelta
        
        if admin_user.email_verification_sent_at:
            if timezone.now() - admin_user.email_verification_sent_at > timedelta(hours=24):
                return Response({
                    'error': 'Verification token has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify email
        admin_user.is_email_verified = True
        admin_user.email_verification_token = None
        admin_user.email_verification_sent_at = None
        admin_user.save()
        
        return Response({
            'message': 'Email verified successfully. You can now login.',
            'admin_user': AdminUserSerializer(admin_user).data
        }, status=status.HTTP_200_OK)
        
    except AdminUser.DoesNotExist:
        return Response({
            'error': 'Invalid verification token.'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Failed to verify email: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """
    Resend verification email
    """
    email = request.data.get('email')
    if not email:
        return Response({
            'error': 'Email is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        admin_user = AdminUser.objects.get(email=email)
        
        if admin_user.is_email_verified:
            return Response({
                'error': 'Email is already verified.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate new verification token
        from django.utils import timezone
        import uuid
        
        verification_token = str(uuid.uuid4())
        admin_user.email_verification_token = verification_token
        admin_user.email_verification_sent_at = timezone.now()
        admin_user.save()
        
        # Send verification email
        send_verification_email(admin_user, verification_token)
        
        return Response({
            'message': 'Verification email sent successfully.'
        }, status=status.HTTP_200_OK)
        
    except AdminUser.DoesNotExist:
        return Response({
            'error': 'Admin user not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Failed to resend verification email: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_token_refresh(request):
    """
    Admin token refresh endpoint
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Decode and verify the refresh token
        refresh = RefreshToken(refresh_token)
        
        # Get the user from the token
        user_id = refresh.payload.get('user_id')
        try:
            user = AdminUser.objects.get(id=user_id)
        except AdminUser.DoesNotExist:
            return Response({
                'error': 'Invalid refresh token.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate new access token
        new_access_token = refresh.access_token
        
        return Response({
            'access': str(new_access_token),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Invalid refresh token.'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAuthenticated])
def admin_dashboard_stats(request):
    """
    Get dashboard statistics
    """
    if not isinstance(request.user, AdminUser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    stats = {
        'pending': VerificationRequest.objects.filter(status='pending').count(),
        'approved': VerificationRequest.objects.filter(status='approved').count(),
        'declined': VerificationRequest.objects.filter(status='declined').count(),
        'archived': VerificationRequest.objects.filter(status='archived').count(),
        'total': VerificationRequest.objects.count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAuthenticated])
def verification_requests_list(request):
    """
    Get all verification requests with filtering
    """
    if not isinstance(request.user, AdminUser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get query parameters for filtering
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    queryset = VerificationRequest.objects.all()
    
    # Filter by status
    if status_filter and status_filter != 'all':
        queryset = queryset.filter(status=status_filter)
    
    # Filter by search query
    if search_query:
        queryset = queryset.filter(
            models.Q(user_full_name__icontains=search_query) |
            models.Q(user_email__icontains=search_query)
        )
    
    # Order by submitted date (newest first)
    queryset = queryset.order_by('-submitted_at')
    
    serializer = VerificationRequestSerializer(queryset, many=True)
    
    return Response({
        'verifications': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAuthenticated])
def accept_verification(request, verification_id):
    """
    Accept a verification request
    """
    if not isinstance(request.user, AdminUser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        verification = VerificationRequest.objects.get(id=verification_id)
        verification.approve(request.user)
        
        # Log the action
        log_admin_action(
            request.user, 
            'approve_verification', 
            'verification_request', 
            verification_id,
            f"Approved verification for {verification.user_email}"
        )
        
        # Send email notification to user
        try:
            subject = 'Verification Approved - MediSync'
            message = f"""
            Dear {verification.user_full_name},
            
            Your verification request has been approved! You can now access all features of your MediSync account.
            
            Thank you for your patience.
            
            Best regards,
            MediSync Admin Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [verification.user_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send approval email: {e}")
        
        return Response({
            'message': 'Verification approved successfully'
        }, status=status.HTTP_200_OK)
        
    except VerificationRequest.DoesNotExist:
        return Response({
            'error': 'Verification request not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAuthenticated])
def decline_verification(request, verification_id):
    """
    Decline a verification request
    """
    if not isinstance(request.user, AdminUser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DeclineVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    reason = serializer.validated_data['reason']
    send_email = serializer.validated_data['send_email']
    
    try:
        verification = VerificationRequest.objects.get(id=verification_id)
        verification.decline(request.user, reason)
        
        # Log the action
        log_admin_action(
            request.user, 
            'decline_verification', 
            'verification_request', 
            verification_id,
            f"Declined verification for {verification.user_email}. Reason: {reason}"
        )
        
        # Send email notification to user if requested
        if send_email:
            try:
                subject = 'Verification Declined - MediSync'
                message = f"""
                Dear {verification.user_full_name},
                
                Your verification request has been declined for the following reason:
                
                {reason}
                
                Please review the requirements and submit a new verification request with the correct documentation.
                
                If you have any questions, please contact our support team.
                
                Best regards,
                MediSync Admin Team
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [verification.user_email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send decline email: {e}")
        
        return Response({
            'message': 'Verification declined successfully'
        }, status=status.HTTP_200_OK)
        
    except VerificationRequest.DoesNotExist:
        return Response({
            'error': 'Verification request not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAuthenticated])
def archive_verification(request, verification_id):
    """
    Archive a verification request
    """
    if not isinstance(request.user, AdminUser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        verification = VerificationRequest.objects.get(id=verification_id)
        verification.archive(request.user)
        
        # Log the action
        log_admin_action(
            request.user, 
            'archive_verification', 
            'verification_request', 
            verification_id,
            f"Archived verification for {verification.user_email}"
        )
        
        return Response({
            'message': 'Verification archived successfully'
        }, status=status.HTTP_200_OK)
        
    except VerificationRequest.DoesNotExist:
        return Response({
            'error': 'Verification request not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAuthenticated])
def update_verification(request, verification_id):
    """
    Update verification request details
    """
    if not isinstance(request.user, AdminUser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        verification = VerificationRequest.objects.get(id=verification_id)
        serializer = VerificationRequestUpdateSerializer(verification, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Log the action
            log_admin_action(
                request.user, 
                'update_verification', 
                'verification_request', 
                verification_id,
                f"Updated verification for {verification.user_email}"
            )
            
            return Response({
                'message': 'Verification updated successfully',
                'verification': VerificationRequestSerializer(verification).data
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except VerificationRequest.DoesNotExist:
        return Response({
            'error': 'Verification request not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAuthenticated])
def system_logs(request):
    """
    Get system logs for audit purposes
    """
    if not isinstance(request.user, AdminUser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Only super admins can view logs
    if not request.user.is_super_admin:
        return Response({
            'error': 'Access denied. Super admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    logs = SystemLog.objects.all()[:100]  # Limit to last 100 logs
    serializer = SystemLogSerializer(logs, many=True)
    
    return Response({
        'logs': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([AdminJWTAuthentication])
@permission_classes([IsAuthenticated])
def serve_verification_document(request, verification_id):
    """
    Serve verification document with appropriate headers for iframe embedding
    """
    try:
        verification = get_object_or_404(VerificationRequest, id=verification_id)
        
        if not verification.verification_document:
            return Response({
                'error': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get the file path
        file_path = verification.verification_document.path
        
        if not os.path.exists(file_path):
            return Response({
                'error': 'File not found on disk'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Open and serve the file with appropriate headers
        file_handle = open(file_path, 'rb')
        response = FileResponse(file_handle, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        
        # Allow iframe embedding and CORS
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET'
        response['Access-Control-Allow-Headers'] = '*'
        
        return response
        
    except Exception as e:
        print(f"Error serving document for verification {verification_id}: {str(e)}")
        return Response({
            'error': f'Failed to serve document: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_verification_email(admin_user, verification_token):
    """
    Send email verification email to admin user
    """
    try:
        # Create verification URL
        verification_url = f"{settings.FRONTEND_URL}/verify-email.html?token={verification_token}"
        
        # Email subject and content
        subject = 'MediSync Admin - Email Verification Required'
        
        # HTML email template
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #286660; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">MediSync Admin</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Healthcare Management System</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; border: 1px solid #e9ecef;">
                    <h2 style="color: #286660; margin-top: 0;">Email Verification Required</h2>
                    
                    <p>Hello {admin_user.full_name},</p>
                    
                    <p>Thank you for registering as an administrator for MediSync. To complete your account setup, please verify your email address by clicking the button below:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" 
                           style="background: #286660; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                            Verify Email Address
                        </a>
                    </div>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="background: #e9ecef; padding: 10px; border-radius: 4px; word-break: break-all; font-family: monospace;">
                        {verification_url}
                    </p>
                    
                    <p><strong>Important:</strong> This verification link will expire in 24 hours for security reasons.</p>
                    
                    <p>If you didn't create this account, please ignore this email.</p>
                    
                    <hr style="border: none; border-top: 1px solid #e9ecef; margin: 30px 0;">
                    
                    <p style="font-size: 14px; color: #666; margin: 0;">
                        Best regards,<br>
                        The MediSync Team
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        MediSync Admin - Email Verification Required
        
        Hello {admin_user.full_name},
        
        Thank you for registering as an administrator for MediSync. To complete your account setup, please verify your email address by visiting the following link:
        
        {verification_url}
        
        Important: This verification link will expire in 24 hours for security reasons.
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        The MediSync Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Verification email sent to {admin_user.email}")
        
    except Exception as e:
        print(f"Failed to send verification email to {admin_user.email}: {e}")
        raise e
