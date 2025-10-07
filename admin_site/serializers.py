from rest_framework import serializers
from .models import AdminUser, VerificationRequest, SystemLog


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['id', 'email', 'full_name', 'is_super_admin', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = AdminUser
        fields = ['email', 'password', 'password_confirm', 'full_name']
        extra_kwargs = {
            'email': {'required': True},
            'full_name': {'required': True}
        }
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if AdminUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("An admin with this email already exists.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        """Create admin user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        admin_user = AdminUser.objects.create_user(
            password=password,
            is_super_admin=False,  # Set to False by default
            **validated_data
        )
        return admin_user


class VerificationRequestSerializer(serializers.ModelSerializer):
    reviewed_by = AdminUserSerializer(read_only=True)
    
    class Meta:
        model = VerificationRequest
        fields = [
            'id', 'user_email', 'user_full_name', 'user_role', 'status',
            'verification_document', 'submitted_at', 'reviewed_at',
            'reviewed_by', 'decline_reason', 'notes'
        ]
        read_only_fields = ['id', 'submitted_at', 'reviewed_at', 'reviewed_by']


class VerificationRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationRequest
        fields = ['status', 'decline_reason', 'notes']


class DeclineVerificationSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)
    send_email = serializers.BooleanField(default=True)


class SystemLogSerializer(serializers.ModelSerializer):
    admin_user = AdminUserSerializer(read_only=True)
    
    class Meta:
        model = SystemLog
        fields = ['id', 'admin_user', 'action', 'target', 'target_id', 'details', 'timestamp']
        read_only_fields = ['id', 'timestamp']
