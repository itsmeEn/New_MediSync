from django.db import models
from django.contrib.auth import get_user_model
from backend.users.models import GeneralDoctorProfile, NurseProfile, PatientProfile
from django.utils import timezone
from datetime import timedelta
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import json


# Custom User Model
# Ensure that the custom user model is used for all user-related operations.
# This is necessary for the queue management system to work with the custom user model.
# This allows us to reference the user model directly without hardcoding the model name.
# This is particularly useful for foreign key relationships and user management.

Users = get_user_model()

#notification management to notify patients about their queue status, appointment reminders, etc.
#notify doctors about the his appointments, patient status, etc.
#motify nurses about the medicine inventory, patient status, etc.
# a realtime notification system that can notify the patients
class Notification(models.Model):
    """
    Notifies the users about their queue status, appointment reminders, etc.
    """
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField(help_text="Notification message.")
    is_read = models.BooleanField(default=False, help_text="Indicates if the notification has been read.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the notification was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the notification was last updated.")

    class Meta:
        ordering = ["-created_at"]
        db_table = "notifications"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user.full_name}: {self.message[:50]}..."  # Display first 50 characters of the message

#queueing system for operations normal queues
class QueueManagement(models.Model):
    """Queue management model for handling patient queues in operations.
    - Each queue is associated with a patient.
    - Tracks the queue number, status, and timestamps for creation and updates.
    - FIFO
    """
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="queue_management")
    queue_number = models.PositiveIntegerField(unique=True)
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True, related_name="queue_management")
    total_patients = models.PositiveIntegerField(default=0, help_text="Total number of patients in the queue.")
    estimated_wait_time = models.DurationField(null=True, blank=True, help_text="Estimated wait time for the patient.")
    expected_patients = models.PositiveIntegerField(default=0, help_text="Expected number of patients in the queue.")   
    actual_wait_time = models.DurationField(null=True, blank=True, help_text="Actual wait time for the patient.")
    finished_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when the queue finished.")
    #department queues like OPD, Billing, Buying Medicines, Appointment 
    department = models.CharField (max_length=100,choices=[
        ("OPD", "Out Patient Department"),
        ("Billing", "Billing"),
        ("Pharmacy", "Pharmacy"),
        ("Appointment", "Appointment"),
    ], help_text="Department for which the queue is managed.")
    status = models.CharField(max_length=50, choices=[
        ("waiting", "Waiting"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ], default="waiting")
    
    #implementation of FIFO 
    position_in_queue = models.PositiveIntegerField(default=0, help_text="Position in the queue.")
    enqueue_time = models.DateTimeField(help_text="Timestamp when the patient was added to the queue."
                                        ,default=timezone.now)
    dequeue_time = models.DateTimeField(null=True, blank=True, help_text="Timestamp when the patient was removed from the queue.")
    started_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when the queue started.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["department", "position_in_queue", "enqueue_time"]
        db_table = "queue_management"
        verbose_name = "Queue Management"
        verbose_name_plural = "Queue Management"
        unique_together = ["department", "queue_number", "patient"] #each patient should have unique queue number when queueing in different departments
        
    #fifo implementtion
    def save(self, *args, **kwargs):
        #auto sign the queueung number in each patients
        if not self.position_in_queue_number:
            last_position = QueueManagement.objects.filter(
                department=self.department, status_in_queue =[
                    'waiting', 'in_progress', 'cancelled'
                ]).aggregate(
                    maximum_position = models.Max("position_in_queue", default=0
                )["position" + 1]
            )
        
        #automaticall assigns the patient queue number
        if not self.queue_number:
            last_queue_number = QueueManagement.objects.filter(
                department=self.department).aggregate(
                    maximum_queue_number = models.Max("queue_number", default=0)
            )
        super().save(*args, **kwargs)
        self.update_queue_positions()
    
    #update the queueu 
    def update_queue_positions(self):
        """
        Update the positions for all waiting patients in the queue.
        """
        waiting_patients = QueueManagement.objects.filter(
            department=self.department, status="waiting"
            ).order_by("enqueue_time")
        
        #ensures that each patient has a position in queueu
        for index, patient in enumerate(waiting_patients, start=1):
            if patient.position_in_queue != index:
                patient.position_in_queue = index
                QueueManagement.objects.filter(id=patient.id).update(position_in_queue=index)
        
        
        #get the patient estimated waiting time
        """
        calculate the estimated waiting time for each patient in the queue.
        """
    def get_estimated_wait_time(self):
        if self.status != "waiting":
            return None
        
        # Calculate average service time
        completed_queues = QueueManagement.objects.filter(
            department=self.department, status="completed",
            started_at__isnull=False, finished_at__isnull=False
        )
        total_service_time = sum([q.finished_at - q.started_at for q in completed_queues], timedelta())
        
        if completed_queues.count() > 0:
            avg_service_time = total_service_time / completed_queues.count()
        else:
            # Use a default value if no one has completed yet
            avg_service_time = timedelta(minutes=15) 

        # Count patients ahead
        patients_ahead_count = QueueManagement.objects.filter(
            department=self.department,
            status__in=["waiting", "in_progress"],
            position_in_queue__lt=self.position_in_queue
        ).count()
        
        return avg_service_time * patients_ahead_count
    
    def started_at(self):
        """
        The time where the service actually started.
        """
        self.status = "in_progress"
        self.started_at = timezone.now()
        self.save()
        
        """
        time when the service is completed
        """
    def completed_at(self):
        self.status = "completed"
        self.completed_at = timezone.now()
        
        if self.started_at:
            self.actual_wait_time = self.started_at - self.enqueue_time
        self.save()
        #update the patients wueue positions or number 
        self.update_queue_positions()
        
    def get_next_in_queue(self):
        """
        Get the next patient in the queue.
        """
        next_patient = QueueManagement.objects.filter(
            department=self.department, status="waiting"
        ).order_by("position_in_queue").first()
        return next_patient
    @classmethod
    def get_queue_by_dept(cls, department):
        """
        Get the queue for a specific department.
        """
        queue = cls.objects.filter(department=department).order_by("position_in_queue")
        
    def __str__(self):
        return f"Queue {self.queue_number} - Patient: {self.patient.full_name}"
    
#medicine inventory management
class MedicineInventory(models.Model):
    """Medicine inventory management model.Tracks the available stock of medicines."""
    inventory = models.ForeignKey(
        NurseProfile, on_delete=models.CASCADE, related_name="medicine_inventory", limit_choices_to={"user__role": "nurse"}
        # This ensures that only nurses or a pharmacist can manage the inventory.
    )
    medicine_name = models.CharField(max_length=100, help_text="Name of the medicine.")
    stock_number = models.PositiveIntegerField(default=0, help_text="Current stock of the medicine.")
    current_stock = models.PositiveIntegerField(default=0, help_text="Current available stock of the medicine.")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit of the medicine.")
    minimum_stock_level = models.PositiveIntegerField(default=0, help_text="Minimum stock level before reordering.")
    expiry_date = models.DateField(null=True, blank=True, help_text="Expiry date of the medicine.")
    batch_number = models.CharField(max_length=50, unique=True, help_text="Batch number of the medicine.")
    last_restocked = models.DateTimeField(auto_now=True, help_text="Last time the medicine was restocked.")
    usage_pattern = models.TextField(
        blank=True, help_text="Description of the usage pattern for the medicine."
    ) #this can be used when the medicine is used frequently or has a specific usage pattern for predicting future stock needs or analytic basta yan siya.
    #notified the nurses about medicine stock, expiration
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True, related_name="medicine_inventory")
    class Meta:
        ordering = ["medicine_name"]
        db_table = "medicine_inventory"
        verbose_name = "Medicine Inventory"
        verbose_name_plural = "Medicine Inventory"

    @property
    def is_expired(self):
        return self.expiry_date and self.expiry_date < timezone.now().date()#this can be used to check if the medicine is expired or not.

    @property
    def is_available(self):
        return self.current_stock > 0 and not self.is_expired

    @property
    def total_value(self):
        return self.current_stock * self.unit_price if self.current_stock else 0.0

    def save(self, *args, **kwargs):
        if self.current_stock < 0:
            raise ValueError("Current stock cannot be negative.")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.medicine_name} - Stock: {self.current_stock}"
    
    #appointment management 
class AppointmentManagement(models.Model):
    """Appointment management model for handling patient appointments."""
    appointment_id = models.AutoField(primary_key=True, help_text="Unique identifier for the appointment.")
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(GeneralDoctorProfile, on_delete=models.CASCADE, related_name="appointments")
    appointment_date = models.DateTimeField(help_text="Date and time of the appointment.")
    appointment_type = models.CharField(
        max_length=50, choices=[
            ("consultation", "Consultation"),
            ("follow_up", "Follow Up"),
            ("emergency", "Emergency"),
        ], default="consultation"
    )
    appointment_time = models.TimeField(help_text="Time of the appointment.")
    queue_number = models.PositiveIntegerField(unique=True, help_text="Queue number for the appointment.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #status of the appointment like scheduled, completed, cancelled, no show
    status = models.CharField(max_length=50, choices=[
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    ], default="scheduled")

    class Meta:
        ordering = ["appointment_date"]
        db_table = "appointment_management"
        verbose_name = "Appointment Management"
        verbose_name_plural = "Appointment Management"

    def __str__(self):
        return f"Appointment {self.id} - Patient: {self.patient.user.full_name} with Dr. {self.doctor.user.full_name}"
    
    def save(self, *args, **kwargs):
        if self.appointment_date < timezone.now():
            raise ValueError("Appointment date cannot be in the past.")
        super().save(*args, **kwargs)
        # This ensures that the appointment date is not in the past.
        # This can be used to check if the appointment is valid or not.
        # This can be used to check if the appointment is scheduled, completed, cancelled, or

#queue for priority patients
# no show.
class PriorityQueue(models.Model):
    """Priority queue model for handling patients with special needs or conditions or age. """
    appointment_id = models.ForeignKey(AppointmentManagement, on_delete=models.CASCADE, related_name="priority_queue")
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="priority_queue")
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True, related_name="priority_queue")
    #prioritty level based on age, condition, or other factors
    priority_level = models.CharField(
        max_length=50, choices=[
            ("pwd", "Person With Disability"),
            ("senior", "Senior Citizen"),
        ], default="senior", help_text="Priority level of the patient in the queue."
    )
    department = models.CharField(max_length=100, choices =[
        ("OPD", "Out Patient Department"),
        ("Billing", "Billing"),
        ("Pharmacy", "Pharmacy"),
        ("Appointment", "Appointment"),
    ], help_text="Department for which the queue is managed.", 
                                  default="OPD")
    
    actual_wait_time = models.DurationField(null=True, blank=True, help_text="Actual wait time for the patient.")
    estimated_wait_time = models.DurationField(null=True, blank=True, help_text="Estimated wait time for the patient.")
    created_at = models.DateTimeField(auto_now_add=True)
    queue_number = models.PositiveIntegerField(unique=True, help_text="Queue number for the priority patient.")
    
    #priority queue specific fields since priority siya di siya mag-undergo sa fifo
    priority_position = models.PositiveIntegerField(default=0, help_text="Position in the priority queue.")
    skip_normal_queues = models.BooleanField(default=False, help_text="Indicates if the patient should be skipped from the FIFO queue.")

    class Meta:
        ordering = ["-priority_level", "priority_position", "created_at"]
        db_table = "priority_queue"
        verbose_name = "Priority Queue"
        verbose_name_plural = "Priority Queues"
        
    def save(self, *args, **kwargs):
        #auto assign queue number
        if not self.queue_number:
            self.queue_number = PriorityQueue.objects.filter(
                department=self.department
            ).aggregate(
                maximum_queue_number = models.Max("queue_number", default=0)
            )['maximum_queue_number'] + 1
            
        #auto assign priority positions
        if not self.priority_position:
            self.priority_position = PriorityQueue.objects.filter(
                department=self.department, priority_level=self.priority_level
            ).count() + 1
        super().save(*args, **kwargs)
       
    """
    Calculate the estimated waiting time priority lists
    """ 
    def get_estimated_wait_time(self):
        if self.status != "waiting":
            return None
        
        # Calculate average service time
        completed_queues = QueueManagement.objects.filter(
            department=self.department, status="completed",
            started_at__isnull=False, finished_at__isnull=False
        )
        total_service_time = sum([q.finished_at - q.started_at for q in completed_queues], timedelta())
        
        if completed_queues.count() > 0:
            avg_service_time = total_service_time / completed_queues.count()
        else:
            # Use a default value if no one has completed yet
            avg_service_time = timedelta(minutes=15) 
            
        #count the patients in higher priority like seniors, pwd something like that
        higher_priority_count = PriorityQueue.objects.filter(
            department=self.department,status_in=[
                "waitng", "in_progress"],
            priority_level__in=["pwd", "senior"],
            priority_position__lt=self.priority_position
        ).count()
        
        if self.priority_level == "senior":
            patients_ahead = higher_priority_count
        elif self.priority_level == "pwd":
            patients_ahead = higher_priority_count
        else: #low priority or just the people in normal queues
            low_priority_count = PriorityQueue.objects.filter(
                department=self.department,status_in=[
                "waitng", "in_progress"]
            ).count()
        
        return avg_service_time * patients_ahead

    def __str__(self):
        return f"Priority Queue - Patient: {self.patient.user.full_name} ({self.priority_level})"
    
#exchanging communications via messaging app
class Conversation(models.Model):
    """
    Conversation model for grouping messages between users.
    """
    participants = models.ManyToManyField(Users, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["-updated_at"]
        db_table = "conversations"
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self):
        participant_names = [p.full_name for p in self.participants.all()]
        return f"Conversation: {', '.join(participant_names)}"

    def get_other_participant(self, user):
        """Get the other participant in a 1-on-1 conversation"""
        return self.participants.exclude(id=user.id).first()
    
    def get_unread_count(self, user):
        """Get unread message count for a specific user"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()
    
    def mark_messages_as_delivered(self, user):
        """Mark messages as delivered for a specific user"""
        undelivered_messages = self.messages.filter(
            is_delivered=False
        ).exclude(sender=user)
        
        for message in undelivered_messages:
            message.is_delivered = True
            message.delivered_at = timezone.now()
            message.save()
    
    def mark_messages_as_read(self, user):
        """Mark messages as read for a specific user"""
        unread_messages = self.messages.filter(
            is_read=False
        ).exclude(sender=user)
        
        for message in unread_messages:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()

class Message(models.Model):
    """
    Enhanced messaging model with file support, reactions, and encryption.
    """ 
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField(help_text="Encrypted message content.")
    encrypted_content = models.TextField(blank=True, help_text="Base64 encoded encrypted content")
    file_attachment = models.FileField(
        upload_to='message_attachments/', 
        blank=True, 
        null=True,
        help_text="Optional file attachment"
    )
    file_name = models.CharField(max_length=255, blank=True, help_text="Original file name")
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    is_read = models.BooleanField(default=False, help_text="Whether the message has been read")
    is_delivered = models.BooleanField(default=False, help_text="Whether the message has been delivered")
    read_at = models.DateTimeField(null=True, blank=True, help_text="When the message was read")
    delivered_at = models.DateTimeField(null=True, blank=True, help_text="When the message was delivered")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the message was sent.")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:        
        ordering = ["created_at"]
        db_table = "messages"
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message from {self.sender.full_name}: {self.content[:50]}..."

    @property
    def has_attachment(self):
        return bool(self.file_attachment)
    
    def encrypt_content(self, plaintext):
        """Encrypt message content using Fernet encryption"""
        try:
            # Get encryption key from settings or generate one
            key = getattr(settings, 'MESSAGE_ENCRYPTION_KEY', None)
            if not key:
                # Generate a new key if none exists (for development)
                key = Fernet.generate_key()
                print(f"Generated new encryption key: {key.decode()}")
            
            if isinstance(key, str):
                key = key.encode()
            
            f = Fernet(key)
            encrypted_data = f.encrypt(plaintext.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            return plaintext  # Fallback to plaintext
    
    def decrypt_content(self):
        """Decrypt message content"""
        try:
            if not self.encrypted_content:
                return self.content
            
            key = getattr(settings, 'MESSAGE_ENCRYPTION_KEY', None)
            if not key:
                return self.content
            
            if isinstance(key, str):
                key = key.encode()
            
            f = Fernet(key)
            encrypted_data = base64.b64decode(self.encrypted_content.encode())
            decrypted_data = f.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return self.content  # Fallback to stored content
    
    def save(self, *args, **kwargs):
        """Override save to encrypt content before saving"""
        if self.content and not self.encrypted_content:
            self.encrypted_content = self.encrypt_content(self.content)
        super().save(*args, **kwargs)
    
    def create_notifications(self):
        """Create notifications for all participants except sender"""
        # Get all participants except sender
        recipients = self.conversation.participants.exclude(id=self.sender.id)
        
        for recipient in recipients:
            MessageNotification.objects.create(
                message=self,
                recipient=recipient,
                notification_type='new_message'
            )

class MessageNotification(models.Model):
    """
    Model for tracking message notifications and delivery status
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="notifications")
    recipient = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="message_notifications")
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('new_message', 'New Message'),
            ('message_delivered', 'Message Delivered'),
            ('message_read', 'Message Read'),
        ],
        default='new_message'
    )
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        db_table = "message_notifications"
        verbose_name = "Message Notification"
        verbose_name_plural = "Message Notifications"
    
    def __str__(self):
        return f"Notification for {self.recipient.full_name}: {self.notification_type}"

class MessageReaction(models.Model):
    """
    Model for message reactions (like, love, etc.)
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="message_reactions")
    reaction_type = models.CharField(
        max_length=20,
        choices=[
            ('like', '👍'),
            ('love', '❤️'),
            ('laugh', '😂'),
            ('wow', '😮'),
            ('sad', '😢'),
            ('angry', '😠'),
        ],
        default='like'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user', 'reaction_type']
        db_table = "message_reactions"
        verbose_name = "Message Reaction"
        verbose_name_plural = "Message Reactions"

    def __str__(self):
        return f"{self.user.full_name} reacted {self.reaction_type} to message"

# Keep the old Messaging model for backward compatibility
class Messaging(models.Model):
    """
    Legacy messaging model - kept for backward compatibility.
    """ 
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="legacy_sent_messages")
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="legacy_received_messages")
    message = models.TextField(help_text="Message content.")    
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the message was sent.")  
    
    class Meta:        
        ordering = ["-created_at"]
        db_table = "messaging"
        verbose_name = "Legacy Messaging"
        verbose_name_plural = "Legacy Messaging"

    def __str__(self):
        return f"From {self.sender.full_name} to {self.receiver.full_name}: {self.message[:50]}..."

#doctor availability management
class DoctorAvailability(models.Model):
    """Doctor availability management for blocking dates and setting schedules."""
    doctor = models.ForeignKey(GeneralDoctorProfile, on_delete=models.CASCADE, related_name="availability")
    date = models.DateField(help_text="Date when doctor is unavailable")
    reason = models.CharField(max_length=255, blank=True, help_text="Reason for unavailability")
    is_blocked = models.BooleanField(default=True, help_text="Whether the date is blocked")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]
        db_table = "doctor_availability"
        verbose_name = "Doctor Availability"
        verbose_name_plural = "Doctor Availability"
        unique_together = ["doctor", "date"]

    def __str__(self):
        return f"Dr. {self.doctor.user.full_name} - {self.date} ({'Blocked' if self.is_blocked else 'Available'})"


class PatientAssignment(models.Model):
    """
    Model for assigning patients to doctors with specific specializations
    """
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="assignments")
    doctor = models.ForeignKey(GeneralDoctorProfile, on_delete=models.CASCADE, related_name="assigned_patients")
    assigned_by = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="patient_assignments", help_text="Nurse who assigned the patient")
    specialization_required = models.CharField(max_length=100, help_text="Required specialization for this assignment")
    assignment_reason = models.TextField(blank=True, help_text="Reason for assignment")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
        help_text="Assignment status"
    )
    assigned_at = models.DateTimeField(auto_now_add=True, help_text="When the patient was assigned")
    accepted_at = models.DateTimeField(null=True, blank=True, help_text="When the doctor accepted the assignment")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="When the consultation was completed")
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='medium',
        help_text="Assignment priority"
    )

    class Meta:
        ordering = ["-assigned_at"]
        db_table = "patient_assignments"
        verbose_name = "Patient Assignment"
        verbose_name_plural = "Patient Assignments"
        unique_together = ['patient', 'doctor', 'assigned_at']

    def __str__(self):
        return f"{self.patient.user.full_name} assigned to Dr. {self.doctor.user.full_name} ({self.specialization_required})"


class ConsultationNotes(models.Model):
    """
    Model for doctor consultation notes
    """
    assignment = models.ForeignKey(PatientAssignment, on_delete=models.CASCADE, related_name="consultation_notes")
    doctor = models.ForeignKey(GeneralDoctorProfile, on_delete=models.CASCADE, related_name="consultation_notes")
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="consultation_notes")
    
    # Consultation details
    chief_complaint = models.TextField(help_text="Patient's main complaint")
    history_of_present_illness = models.TextField(help_text="Detailed history of the current illness")
    physical_examination = models.TextField(help_text="Physical examination findings")
    diagnosis = models.TextField(help_text="Doctor's diagnosis")
    treatment_plan = models.TextField(help_text="Recommended treatment plan")
    medications_prescribed = models.TextField(blank=True, help_text="Medications prescribed")
    follow_up_instructions = models.TextField(blank=True, help_text="Follow-up instructions for the patient")
    additional_notes = models.TextField(blank=True, help_text="Any additional notes")
    
    # Status and timestamps
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('completed', 'Completed'),
            ('reviewed', 'Reviewed'),
        ],
        default='draft',
        help_text="Status of the consultation notes"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the notes were created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the notes were last updated")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="When the consultation was completed")

    class Meta:
        ordering = ["-created_at"]
        db_table = "consultation_notes"
        verbose_name = "Consultation Notes"
        verbose_name_plural = "Consultation Notes"

    def __str__(self):
        return f"Consultation notes for {self.patient.user.full_name} by Dr. {self.doctor.user.full_name}"