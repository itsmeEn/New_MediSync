from django.contrib import admin
from .models import (
    AppointmentManagement,
    MedicineInventory,
    Messaging,
    Notification,
    PriorityQueue,
    QueueManagement,
    Conversation,
    Message,
    MessageReaction,
    DoctorAvailability,
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__full_name', 'message')


@admin.register(QueueManagement)
class QueueManagementAdmin(admin.ModelAdmin):
    list_display = ('queue_number', 'patient', 'department', 'status', 'created_at')
    list_filter = ('department', 'status')
    search_fields = ('patient__user__full_name', 'queue_number')


@admin.register(MedicineInventory)
class MedicineInventoryAdmin(admin.ModelAdmin):
    list_display = ('medicine_name', 'current_stock', 'unit_price', 'expiry_date', 'is_expired')
    list_filter = ('expiry_date',)
    search_fields = ('medicine_name', 'batch_number')
    readonly_fields = ('is_expired', 'is_available', 'total_value')


@admin.register(AppointmentManagement)
class AppointmentManagementAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'patient', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date', 'doctor')
    search_fields = ('patient__user__full_name', 'doctor__user__full_name')


@admin.register(PriorityQueue)
class PriorityQueueAdmin(admin.ModelAdmin):
    list_display = ('patient', 'priority_level', 'queue_number', 'created_at')
    list_filter = ('priority_level',)
    search_fields = ('patient__user__full_name',)


@admin.register(Messaging)
class MessagingAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sender__full_name', 'receiver__full_name', 'message')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('participants__full_name',)
    filter_horizontal = ('participants',)
    
    def get_participants(self, obj):
        return ', '.join([p.full_name for p in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content_preview', 'has_attachment', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'conversation')
    search_fields = ('sender__full_name', 'content')
    readonly_fields = ('has_attachment',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__full_name', 'message__content')


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'is_blocked', 'reason', 'created_at')
    list_filter = ('is_blocked', 'date', 'created_at')
    search_fields = ('doctor__user__full_name', 'reason')
