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
    MessageNotification,
    PatientAssignment,
    ConsultationNotes,
    QueueSchedule,
    QueueStatus,
    QueueStatusLog,
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


@admin.register(MessageNotification)
class MessageNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'notification_type', 'is_sent', 'created_at')
    list_filter = ('notification_type', 'is_sent', 'created_at')
    search_fields = ('recipient__full_name', 'message__content')


@admin.register(PatientAssignment)
class PatientAssignmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'assigned_at', 'status', 'priority')
    list_filter = ('status', 'priority', 'assigned_at', 'doctor')
    search_fields = ('patient__user__full_name', 'doctor__user__full_name')
    readonly_fields = ('assigned_at',)


@admin.register(ConsultationNotes)
class ConsultationNotesAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at', 'doctor__user__full_name')
    search_fields = ('patient__user__full_name', 'doctor__user__full_name', 'chief_complaint')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('assignment', 'doctor', 'patient', 'status')
        }),
        ('Consultation Details', {
            'fields': ('chief_complaint', 'history_of_present_illness', 'physical_examination', 'diagnosis')
        }),
        ('Treatment', {
            'fields': ('treatment_plan', 'medications_prescribed', 'follow_up_instructions', 'additional_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(QueueSchedule)
class QueueScheduleAdmin(admin.ModelAdmin):
    list_display = ('department', 'nurse', 'start_time', 'end_time', 'is_active', 'manual_override', 'override_status')
    list_filter = ('department', 'is_active', 'manual_override', 'override_status')
    search_fields = ('nurse__user__full_name', 'department')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('department', 'nurse', 'is_active')
        }),
        ('Schedule Settings', {
            'fields': ('start_time', 'end_time', 'days_of_week')
        }),
        ('Manual Override', {
            'fields': ('manual_override', 'override_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(QueueStatus)
class QueueStatusAdmin(admin.ModelAdmin):
    list_display = ('department', 'is_open', 'current_serving', 'total_waiting', 'status_message', 'last_updated_at')
    list_filter = ('department', 'is_open', 'last_updated_at')
    search_fields = ('department', 'status_message')
    readonly_fields = ('last_updated_at', 'created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('department', 'is_open', 'status_message')
        }),
        ('Queue Details', {
            'fields': ('current_serving', 'total_waiting', 'estimated_wait_time')
        }),
        ('Update Information', {
            'fields': ('last_updated_by', 'last_updated_at', 'created_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(QueueStatusLog)
class QueueStatusLogAdmin(admin.ModelAdmin):
    list_display = ('department', 'previous_status', 'new_status', 'change_reason', 'changed_by', 'changed_at')
    list_filter = ('department', 'change_reason', 'changed_at', 'new_status')
    search_fields = ('department', 'changed_by__full_name', 'additional_notes')
    readonly_fields = ('changed_at',)
    
    fieldsets = (
        ('Status Change', {
            'fields': ('department', 'previous_status', 'new_status', 'change_reason')
        }),
        ('Change Information', {
            'fields': ('changed_by', 'changed_at', 'additional_notes')
        })
    )
