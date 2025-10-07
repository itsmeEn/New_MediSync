from rest_framework import serializers
from .models import User, GeneralDoctorProfile, NurseProfile, PatientProfile
from django.utils import timezone
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
            'is_verified', 'verification_status', 'profile_picture', 'verification_document',
            'doctor_profile', 'nurse_profile', 'patient_profile',
            'date_joined', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'updated_at']


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
    A separate serializer for updating only the profile picture.
    """
    class Meta:
        model = User
        fields = ["profile_picture"]

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