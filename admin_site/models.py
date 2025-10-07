from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from .managers import AdminUserManager

class AdminUser(AbstractUser):
    """
    Admin user model for the separate admin site.
    """
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    is_super_admin = models.BooleanField(default=False)
    
    # Email verification fields
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    objects = AdminUserManager()
    
    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    # Fix reverse accessor conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='admin_user_set',
        related_query_name='admin_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='admin_user_set',
        related_query_name='admin_user',
    )


class VerificationRequest(models.Model):
    """
    Model to track verification requests from the main MediSync application.
    """
    
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"
        ARCHIVED = "archived", "Archived"
    
    # Reference to the main MediSync user (using email as foreign key)
    user_email = models.EmailField()
    user_full_name = models.CharField(max_length=255)
    user_role = models.CharField(max_length=20)  # doctor, nurse, patient
    
    # Verification details
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    verification_document = models.FileField(upload_to='verification_documents/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True)
    decline_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = "admin_verification_requests"
        verbose_name = "Verification Request"
        verbose_name_plural = "Verification Requests"
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Verification for {self.user_full_name} ({self.user_email}) - {self.status}"
    
    def approve(self, admin_user):
        """Approve the verification request."""
        self.status = self.Status.APPROVED
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()
        
        # Update the actual user's verification status
        try:
            from backend.users.models import User
            user = User.objects.get(email=self.user_email)
            user.verification_status = 'approved'
            user.save()
        except User.DoesNotExist:
            # User might not exist in the main app, that's okay
            pass
    
    def decline(self, admin_user, reason=""):
        """Decline the verification request."""
        self.status = self.Status.DECLINED
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.decline_reason = reason
        self.save()
        
        # Update the actual user's verification status
        try:
            from backend.users.models import User
            user = User.objects.get(email=self.user_email)
            user.verification_status = 'declined'
            user.save()
        except User.DoesNotExist:
            # User might not exist in the main app, that's okay
            pass
    
    def archive(self, admin_user):
        """Archive the verification request."""
        self.status = self.Status.ARCHIVED
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()


class SystemLog(models.Model):
    """
    Model to track admin actions for audit purposes.
    """
    admin_user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=100)  # e.g., "verification_request"
    target_id = models.IntegerField()
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "admin_system_logs"
        verbose_name = "System Log"
        verbose_name_plural = "System Logs"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.admin_user.full_name} - {self.action} - {self.timestamp}"
