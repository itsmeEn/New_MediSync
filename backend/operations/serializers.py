from rest_framework import serializers
from .models import AppointmentManagement, QueueManagement, PriorityQueue, Notification, Messaging, Conversation, Message, MessageReaction, MessageNotification, MedicineInventory, PatientAssignment, ConsultationNotes
from backend.users.models import User

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_appointments = serializers.IntegerField()
    total_patients = serializers.IntegerField()
    normal_queue = serializers.IntegerField()
    priority_queue = serializers.IntegerField()
    notifications = serializers.IntegerField()
    pending_assessment = serializers.IntegerField()

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    
    class Meta:
        model = AppointmentManagement
        fields = ['appointment_id', 'patient_name', 'doctor_name', 'appointment_date', 'status', 'appointment_type']

class QueueSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    
    class Meta:
        model = QueueManagement
        fields = ['queue_number', 'patient_name', 'department', 'status', 'position_in_queue', 'enqueue_time']

class PriorityQueueSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    
    class Meta:
        model = PriorityQueue
        fields = ['queue_number', 'patient_name', 'priority_level', 'department', 'priority_position']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']

# NurseChartSerializer commented out until NurseChart model is fully implemented
# class NurseChartSerializer(serializers.ModelSerializer):
#     patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
#     nurse_name = serializers.CharField(source='nurse.user.full_name', read_only=True)
#     
#     class Meta:
#         model = NurseChart
#         fields = ['id', 'patient_name', 'nurse_name', 'chief_complaint', 'status', 'priority', 'created_at']

# Messaging Serializers
class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information in conversations"""
    class Meta:
        model = User
        fields = ['id', 'full_name', 'role', 'profile_picture']

class MessageReactionSerializer(serializers.ModelSerializer):
    """Serializer for message reactions"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'reaction_type', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages"""
    sender = UserSerializer(read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    has_attachment = serializers.ReadOnlyField()
    decrypted_content = serializers.SerializerMethodField()
    is_delivered = serializers.ReadOnlyField()
    read_at = serializers.ReadOnlyField()
    delivered_at = serializers.ReadOnlyField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'decrypted_content', 'file_attachment', 'file_name', 'file_size', 
                 'has_attachment', 'is_read', 'is_delivered', 'read_at', 'delivered_at', 
                 'created_at', 'updated_at', 'reactions']
    
    def get_decrypted_content(self, obj):
        """Return decrypted content for the message"""
        return obj.decrypt_content()

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'other_participant', 'last_message', 
                 'unread_count', 'created_at', 'updated_at', 'is_active']
    
    def get_last_message(self, obj):
        """Get the last message in the conversation"""
        last_msg = obj.messages.last()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None
    
    def get_unread_count(self, obj):
        """Get unread message count for the current user"""
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
    
    def get_other_participant(self, obj):
        """Get the other participant in a 1-on-1 conversation"""
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            if other:
                return UserSerializer(other).data
        return None

class CreateMessageSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages"""
    class Meta:
        model = Message
        fields = ['content', 'file_attachment']
    
    def validate_file_attachment(self, value):
        """Validate file attachment"""
        if value:
            # Check file size (max 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("File size cannot exceed 10MB")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 
                           'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("File type not allowed")
        
        return value

class CreateReactionSerializer(serializers.ModelSerializer):
    """Serializer for creating message reactions"""
    class Meta:
        model = MessageReaction
        fields = ['reaction_type']

class MessageNotificationSerializer(serializers.ModelSerializer):
    """Serializer for message notifications"""
    message = MessageSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = MessageNotification
        fields = ['id', 'message', 'recipient', 'notification_type', 'is_sent', 'sent_at', 'created_at']

class MedicineInventorySerializer(serializers.ModelSerializer):
    """Serializer for medicine inventory"""
    stock_level = serializers.SerializerMethodField()

    class Meta:
        model = MedicineInventory
        fields = ['id', 'medicine_name', 'stock_number', 'current_stock', 'unit_price',
                  'minimum_stock_level', 'expiry_date', 'batch_number', 'last_restocked',
                  'usage_pattern', 'stock_level']

    def get_stock_level(self, obj):
        """Calculate stock level based on current stock and minimum level"""
        if obj.current_stock == 0:
            return 'out_of_stock'
        elif obj.current_stock <= obj.minimum_stock_level:
            return 'low_stock'
        else:
            return 'in_stock'


class PatientAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for patient assignments"""
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.full_name', read_only=True)
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)
    doctor_id = serializers.IntegerField(source='doctor.id', read_only=True)

    class Meta:
        model = PatientAssignment
        fields = ['id', 'patient', 'patient_id', 'patient_name', 'doctor', 'doctor_id', 'doctor_name',
                  'assigned_by', 'assigned_by_name', 'specialization_required', 'assignment_reason',
                  'status', 'assigned_at', 'accepted_at', 'completed_at', 'priority']

    def create(self, validated_data):
        """Create a new patient assignment"""
        return PatientAssignment.objects.create(**validated_data)


class ConsultationNotesSerializer(serializers.ModelSerializer):
    """Serializer for consultation notes"""
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    assignment_id = serializers.IntegerField(source='assignment.id', read_only=True)

    class Meta:
        model = ConsultationNotes
        fields = ['id', 'assignment', 'assignment_id', 'doctor', 'patient', 'patient_name', 'doctor_name',
                  'chief_complaint', 'history_of_present_illness', 'physical_examination', 'diagnosis',
                  'treatment_plan', 'medications_prescribed', 'follow_up_instructions', 'additional_notes',
                  'status', 'created_at', 'updated_at', 'completed_at']

    def create(self, validated_data):
        """Create new consultation notes"""
        return ConsultationNotes.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update consultation notes"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
