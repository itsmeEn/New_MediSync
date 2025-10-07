"""
Async services for users module.
This module provides async implementations of user management functionality.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db import transaction
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.tokens import RefreshToken

from .models import GeneralDoctorProfile, NurseProfile, PatientProfile, VerificationRequest
from utils.async_db import AsyncModelManager, AsyncTransactionManager, async_safe

User = get_user_model()
logger = logging.getLogger(__name__)

class AsyncUserService:
    """Async service for user management."""
    
    @staticmethod
    @async_safe(timeout=30)
    async def create_user_with_profile(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a user with their profile asynchronously."""
        try:
            async def create_user_operation():
                # Create user
                user = await AsyncModelManager.create_object(
                    User,
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    phone_number=user_data.get('phone_number', ''),
                    date_of_birth=user_data.get('date_of_birth'),
                    gender=user_data.get('gender', 'other'),
                    address=user_data.get('address', '')
                )
                
                # Set password
                await sync_to_async(user.set_password)(user_data['password'])
                await sync_to_async(user.save)()
                
                # Create appropriate profile
                if user.role == 'doctor':
                    await AsyncModelManager.create_object(
                        GeneralDoctorProfile,
                        user=user,
                        license_number=user_data.get('license_number'),
                        specialization=user_data.get('specialization')
                    )
                elif user.role == 'nurse':
                    await AsyncModelManager.create_object(
                        NurseProfile,
                        user=user,
                        license_number=user_data.get('license_number'),
                        department=user_data.get('department')
                    )
                elif user.role == 'patient':
                    await AsyncModelManager.create_object(
                        PatientProfile,
                        user=user,
                        blood_type=user_data.get('blood_type', 'unknown'),
                        medical_condition=user_data.get('medical_condition', ''),
                        medication=user_data.get('medication', '')
                    )
                
                return user
            
            # Execute in atomic transaction
            user = await AsyncTransactionManager.atomic_operation([create_user_operation])
            user = user[0]  # Get the user from the results list
            
            # Generate JWT tokens
            refresh = await sync_to_async(RefreshToken.for_user)(user)
            
            return {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }
        except Exception as e:
            logger.error(f"Error creating user with profile: {str(e)}")
            raise

    @staticmethod
    @async_safe(timeout=30)
    async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user asynchronously."""
        try:
            # Get user
            user = await AsyncModelManager.get_object_or_none(User, email=email)
            if not user:
                return None
            
            # Check password
            password_valid = await sync_to_async(user.check_password)(password)
            if not password_valid:
                return None
            
            # Generate tokens
            refresh = await sync_to_async(RefreshToken.for_user)(user)
            
            return {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_verified': user.is_verified
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise

    @staticmethod
    @async_safe(timeout=30)
    async def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile asynchronously."""
        try:
            user = await AsyncModelManager.get_object_or_none(User, id=user_id)
            if not user:
                return None
            
            profile_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'phone_number': user.phone_number,
                'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
                'gender': user.gender,
                'address': user.address,
                'is_verified': user.is_verified,
                'profile_picture': user.profile_picture.url if user.profile_picture else None
            }
            
            # Get role-specific profile
            if user.role == 'doctor':
                doctor_profile = await AsyncModelManager.get_object_or_none(
                    GeneralDoctorProfile, user=user
                )
                if doctor_profile:
                    profile_data.update({
                        'license_number': doctor_profile.license_number,
                        'specialization': doctor_profile.specialization
                    })
            elif user.role == 'nurse':
                nurse_profile = await AsyncModelManager.get_object_or_none(
                    NurseProfile, user=user
                )
                if nurse_profile:
                    profile_data.update({
                        'license_number': nurse_profile.license_number,
                        'department': nurse_profile.department
                    })
            elif user.role == 'patient':
                patient_profile = await AsyncModelManager.get_object_or_none(
                    PatientProfile, user=user
                )
                if patient_profile:
                    profile_data.update({
                        'blood_type': patient_profile.blood_type,
                        'medical_condition': patient_profile.medical_condition,
                        'medication': patient_profile.medication
                    })
            
            return profile_data
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise

    @staticmethod
    @async_safe(timeout=30)
    async def update_user_profile(user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile asynchronously."""
        try:
            user = await AsyncModelManager.get_object_or_none(User, id=user_id)
            if not user:
                raise ValueError("User not found")
            
            # Update user fields
            user_fields = ['first_name', 'last_name', 'phone_number', 'address']
            user_updates = {k: v for k, v in update_data.items() if k in user_fields}
            
            if user_updates:
                await AsyncModelManager.update_object(user, **user_updates)
            
            # Update role-specific profile
            if user.role == 'doctor':
                doctor_profile = await AsyncModelManager.get_object_or_none(
                    GeneralDoctorProfile, user=user
                )
                if doctor_profile:
                    doctor_fields = ['specialization']
                    doctor_updates = {k: v for k, v in update_data.items() if k in doctor_fields}
                    if doctor_updates:
                        await AsyncModelManager.update_object(doctor_profile, **doctor_updates)
            
            elif user.role == 'nurse':
                nurse_profile = await AsyncModelManager.get_object_or_none(
                    NurseProfile, user=user
                )
                if nurse_profile:
                    nurse_fields = ['department']
                    nurse_updates = {k: v for k, v in update_data.items() if k in nurse_fields}
                    if nurse_updates:
                        await AsyncModelManager.update_object(nurse_profile, **nurse_updates)
            
            elif user.role == 'patient':
                patient_profile = await AsyncModelManager.get_object_or_none(
                    PatientProfile, user=user
                )
                if patient_profile:
                    patient_fields = ['blood_type', 'medical_condition', 'medication']
                    patient_updates = {k: v for k, v in update_data.items() if k in patient_fields}
                    if patient_updates:
                        await AsyncModelManager.update_object(patient_profile, **patient_updates)
            
            # Return updated profile
            return await AsyncUserService.get_user_profile(user_id)
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise

    @staticmethod
    @async_safe(timeout=30)
    async def change_user_password(user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password asynchronously."""
        try:
            user = await AsyncModelManager.get_object_or_none(User, id=user_id)
            if not user:
                raise ValueError("User not found")
            
            # Verify old password
            password_valid = await sync_to_async(user.check_password)(old_password)
            if not password_valid:
                raise ValueError("Invalid old password")
            
            # Set new password
            await sync_to_async(user.set_password)(new_password)
            await sync_to_async(user.save)()
            
            return True
        except Exception as e:
            logger.error(f"Error changing user password: {str(e)}")
            raise

    @staticmethod
    @async_safe(timeout=30)
    async def send_password_reset_email(email: str) -> bool:
        """Send password reset email asynchronously."""
        try:
            user = await AsyncModelManager.get_object_or_none(User, email=email)
            if not user:
                return False  # Don't reveal if email exists
            
            # Generate reset token
            token = await sync_to_async(default_token_generator.make_token)(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Send email asynchronously
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            await sync_to_async(send_mail)(
                subject="Password Reset Request",
                message=f"Click the following link to reset your password: {reset_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
            
            return True
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            raise

    @staticmethod
    @async_safe(timeout=30)
    async def reset_password(uidb64: str, token: str, new_password: str) -> bool:
        """Reset user password asynchronously."""
        try:
            # Decode user ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = await AsyncModelManager.get_object_or_none(User, pk=uid)
            
            if not user:
                return False
            
            # Verify token
            token_valid = await sync_to_async(default_token_generator.check_token)(user, token)
            if not token_valid:
                return False
            
            # Set new password
            await sync_to_async(user.set_password)(new_password)
            await sync_to_async(user.save)()
            
            return True
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            raise

class AsyncVerificationService:
    """Async service for user verification."""
    
    @staticmethod
    @async_safe(timeout=30)
    async def submit_verification_request(user_id: int, document_data: Dict[str, Any]) -> bool:
        """Submit verification request asynchronously."""
        try:
            user = await AsyncModelManager.get_object_or_none(User, id=user_id)
            if not user:
                raise ValueError("User not found")
            
            # Check for existing request
            existing_request = await AsyncModelManager.get_object_or_none(
                VerificationRequest, user=user, status='pending'
            )
            
            if existing_request:
                # Update existing request
                await AsyncModelManager.update_object(
                    existing_request,
                    document_type=document_data['document_type'],
                    document_file=document_data['document_file'],
                    submitted_at=asyncio.get_event_loop().time()
                )
            else:
                # Create new request
                await AsyncModelManager.create_object(
                    VerificationRequest,
                    user=user,
                    document_type=document_data['document_type'],
                    document_file=document_data['document_file'],
                    status='pending'
                )
            
            return True
        except Exception as e:
            logger.error(f"Error submitting verification request: {str(e)}")
            raise

    @staticmethod
    @async_safe(timeout=30)
    async def verify_user(user_id: int) -> bool:
        """Verify user asynchronously."""
        try:
            user = await AsyncModelManager.get_object_or_none(User, id=user_id)
            if not user:
                raise ValueError("User not found")
            
            # Update user verification status
            await AsyncModelManager.update_object(user, is_verified=True)
            
            # Update verification request status
            verification_request = await AsyncModelManager.get_object_or_none(
                VerificationRequest, user=user, status='pending'
            )
            
            if verification_request:
                await AsyncModelManager.update_object(
                    verification_request, status='approved'
                )
            
            return True
        except Exception as e:
            logger.error(f"Error verifying user: {str(e)}")
            raise