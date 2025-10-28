from rest_framework import serializers
from .models import User, GeneralDoctorProfile, NurseProfile, PatientProfile
from django.utils import timezone
# Removed image processing imports; profile picture uploads are deprecated
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
    # New: hospital selection is required; accept hospital_id from admin_site
    hospital_id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "full_name", "role", "date_of_birth", "gender", 
            "password", "password2", "license_number", "specialization", "department",
            "verification_document", "hospital_id"
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
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number.")
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

        # Hospital validation: require an ACTIVE hospital
        hospital_id = attrs.get('hospital_id')
        if not hospital_id:
            raise serializers.ValidationError({"hospital": "Please select your hospital."})
        # Avoid import path issues by using Django app registry
        from django.apps import apps
        Hospital = apps.get_model('admin_site', 'Hospital')
        try:
            hospital = Hospital.objects.get(id=hospital_id, status__iexact=Hospital.Status.ACTIVE)
        except Hospital.DoesNotExist:
            raise serializers.ValidationError({"hospital": "Selected hospital is not active or does not exist."})
        # Propagate authoritative hospital details to the user
        attrs['hospital_name'] = hospital.official_name
        attrs['hospital_address'] = hospital.address

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        validated_data.pop("license_number", None)
        validated_data.pop("specialization", None)
        validated_data.pop("department", None)
        validated_data.pop("hospital_id", None)
        user = User.objects.create_user(**validated_data)
        return user

# Removed: ProfilePictureSerializer (profile picture uploads are deprecated)

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
    Serializer for updating user profile information including hospital details,
    and doctor-specific fields (specialization, license_number) when applicable.
    """
    specialization = serializers.CharField(required=False, allow_blank=True)
    license_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email', 'full_name', 'date_of_birth', 'gender', 
            'hospital_name', 'hospital_address',
            'specialization', 'license_number'
        ]
        read_only_fields = ['email']  # Email should not be updated through this endpoint

    def update(self, instance, validated_data):
        # Extract doctor-specific fields
        specialization = validated_data.pop('specialization', None)
        license_number = validated_data.pop('license_number', None)

        # Update top-level User fields first
        instance = super().update(instance, validated_data)

        # Update doctor profile if user is a doctor
        try:
            from .models import GeneralDoctorProfile
            if getattr(instance, 'role', None) == 'doctor':
                # Ensure doctor profile exists
                doctor_profile = getattr(instance, 'doctor_profile', None)
                if doctor_profile is None:
                    doctor_profile = GeneralDoctorProfile.objects.create(user=instance)

                changed = False
                if specialization is not None:
                    doctor_profile.specialization = specialization
                    changed = True
                if license_number is not None:
                    doctor_profile.license_number = license_number
                    changed = True
                if changed:
                    doctor_profile.save()
        except Exception:
            # Silently ignore to avoid breaking generic profile updates; logs handled in views
            pass

        return instance


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