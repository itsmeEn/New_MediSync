from rest_framework import serializers
from .models import User, GeneralDoctorProfile, NurseProfile, PatientProfile
from django.utils import timezone
from .image_utils import ImageProcessor, process_profile_picture
import re


class GeneralDoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralDoctorProfile
        fields = "__all__"


class NurseProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseProfile
        fields = "__all__"


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = "__all__"
        read_only_fields = ["user"]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model - used for general user data representation
    """
    doctor_profile = GeneralDoctorProfileSerializer(read_only=True)
    nurse_profile = NurseProfileSerializer(read_only=True)
    patient_profile = PatientProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role', 'date_of_birth', 'gender',
            'hospital_name', 'hospital_address', 'is_verified', 'verification_status', 
            'profile_picture', 'verification_document', 'doctor_profile', 'nurse_profile', 
            'patient_profile', 'two_factor_enabled', 'date_joined', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'updated_at', 'two_factor_enabled']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users. It handles passwords and role-based
    validation.
    """
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    license_number = serializers.CharField(required=False, write_only=True)
    specialization = serializers.CharField(required=False, write_only=True)
    department = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "full_name", "role", "date_of_birth", "gender", 
            "password", "password2", "license_number", "specialization", "department",
            "profile_picture", "verification_document"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        """
        Validate password requirements:
        - At least 8 characters long
        - Contains at least one letter and one number
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        # Check if password contains at least one letter and one number
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        return value

    def validate_verification_document(self, value):
        """
        Validate verification document file type
        """
        if value:
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Only PDF, JPG, and PNG files are allowed.")
            
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("File size must be less than 5MB.")
        
        return value

    def validate_email(self, value):
        """
        Validate email uniqueness
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # ⚠️ Enforce role-based field requirements
        role = attrs.get('role')
        if role == 'doctor' and not (attrs.get('license_number') and attrs.get('specialization')):
            raise serializers.ValidationError({"role_fields": "License number and specialization are required for doctors."})
        if role == 'nurse' and not attrs.get('license_number'):
            raise serializers.ValidationError({"role_fields": "License number is required for nurses."})
        if role == 'nurse' and not attrs.get('department'):
            raise serializers.ValidationError({"role_fields": "Department is required for nurses."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        validated_data.pop("license_number", None)
        validated_data.pop("specialization", None)
        validated_data.pop("department", None)
        
        user = User.objects.create_user(**validated_data)
        return user

class ProfilePictureSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for updating profile pictures with validation and optimization.
    """
    class Meta:
        model = User
        fields = ["profile_picture"]
    
    def validate_profile_picture(self, value):
        """
        Comprehensive validation for profile picture uploads.
        """
        if value:
            try:
                # Use the ImageProcessor for validation
                validation_result = ImageProcessor.validate_image_file(value)
                
                # Log any warnings
                if validation_result.get('warnings'):
                    # In a production environment, you might want to log these warnings
                    pass
                
                return value
                
            except Exception as e:
                raise serializers.ValidationError(str(e))
        
        return value
    
    def update(self, instance, validated_data):
        """
        Update user profile picture with optimization.
        """
        profile_picture = validated_data.get('profile_picture')
        
        if profile_picture:
            try:
                # Process and optimize the image
                optimized_image = process_profile_picture(profile_picture, instance.id)
                validated_data['profile_picture'] = optimized_image
                
            except Exception as e:
                raise serializers.ValidationError(f"Failed to process image: {str(e)}")
        
        return super().update(instance, validated_data)

class VerificationDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for updating verification document and verification status
    """
    class Meta:
        model = User
        fields = ["verification_document", "is_verified", "verification_status"]

    def validate_verification_document(self, value):
        """
        Validate verification document file type
        """
        if value:
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Only PDF, JPG, and PNG files are allowed.")
            
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("File size must be less than 5MB.")
        
        return value


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information including hospital details
    """
    class Meta:
        model = User
        fields = [
            'email', 'full_name', 'date_of_birth', 'gender', 
            'hospital_name', 'hospital_address'
        ]
        read_only_fields = ['email']  # Email should not be updated through this endpoint


class TwoFactorEnableSerializer(serializers.Serializer):
    """
    Serializer for initiating 2FA setup
    """
    pass  # No input required for initial setup


class TwoFactorVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying and activating 2FA
    """
    otp_code = serializers.CharField(
        max_length=6,
        min_length=6,
        required=True,
        help_text="6-digit OTP code from authenticator app"
    )

    def validate_otp_code(self, value):
        """Validate that OTP code is 6 digits"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must contain only digits.")
        return value


class TwoFactorDisableSerializer(serializers.Serializer):
    """
    Serializer for disabling 2FA
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="User password for verification"
    )


class TwoFactorLoginSerializer(serializers.Serializer):
    """
    Serializer for 2FA login verification
    """
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(
        max_length=6,
        min_length=6,
        required=True,
        help_text="6-digit OTP code from authenticator app"
    )

    def validate_otp_code(self, value):
        """Validate that OTP code is 6 digits"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must contain only digits.")
        return value