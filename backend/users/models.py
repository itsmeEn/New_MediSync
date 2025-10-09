from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from .managers import CustomUserManager
from .image_utils import get_upload_path, validate_profile_picture

class User(AbstractUser):
    """
    Custom user model.
    - Uses email as the unique identifier.
    - Adds role, full_name, and other profile fields.
    - Inherits fields like password, last_login, is_superuser from AbstractUser.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        NURSE = "nurse", "Nurse"
        DOCTOR = "doctor", "Doctor"
        PATIENT = "patient", "Patient"
        
    profile_picture = models.ImageField(
        upload_to=get_upload_path,
        blank=True,
        null=True,
        validators=[validate_profile_picture],
        help_text="Upload a profile picture (JPG, PNG, or WebP, max 5MB)"
    )
    verification_document = models.FileField(
        upload_to='verification_documents/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Upload a PDF, JPG, or PNG file for identity verification"
    )
    # AbstractUser has a 'username' field. We set it to None to indicate
    username = None
    email = models.EmailField("email address", unique=True)

    # Custom fields
    role = models.CharField(max_length=10, choices=Role.choices)
    full_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    hospital_name = models.CharField(max_length=255, blank=True, help_text="Hospital or medical facility name")
    hospital_address = models.TextField(blank=True, help_text="Hospital address")
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('not_submitted', 'Not Submitted'),
            ('pending', 'Pending Admin Review'),
            ('approved', 'Approved'),
            ('declined', 'Declined'),
        ],
        default='not_submitted'
    )
    updated_at = models.DateTimeField(auto_now=True)  # `date_joined` from AbstractUser serves as `created_at`

    USERNAME_FIELD = "email"
    # 'email' and 'password' are required by default.
    # These fields will be prompted for when using the `createsuperuser` command.
    REQUIRED_FIELDS = ["full_name", "role"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email

    def clean(self):
        from django.core.exceptions import ValidationError
        import re
        
        # Password validation for alphanumeric combination with at least 8 characters
        if self.password and len(self.password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        if self.password and not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$', self.password):
            raise ValidationError("Password must contain at least one letter and one number.")


class GeneralDoctorProfile(models.Model):
    """Profile model for users with the 'doctor' role."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")
    license_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True)
    available_for_consultation = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "general_doctor_profiles"
        verbose_name = "General Doctor Profile"
        verbose_name_plural = "General Doctor Profiles"

    def __str__(self):
        return f"Dr. {self.user.full_name} - {self.specialization}"


class NurseProfile(models.Model):
    """Profile model for users with the 'nurse' role."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="nurse_profile")
    license_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, help_text="Department where the nurse works")

    class Meta:
        db_table = "nurse_profiles"
        verbose_name = "Nurse Profile"
        verbose_name_plural = "Nurse Profiles"

    def __str__(self):
        return f"Nurse {self.user.full_name}"
    
    #patient profile
class PatientProfile(models.Model): #can be the content of medical history
    """Profile model for users with the 'patient' role."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_profile")
    

    # Note: Name, Age, and Gender are sourced from the related User model.
    # Age can be calculated from user.date_of_birth.
    #this is for patient demographics for predictive analytics
    class BloodType(models.TextChoices):
        A_POSITIVE = "A+", "A+"
        A_NEGATIVE = "A-", "A-"
        B_POSITIVE = "B+", "B+"
        B_NEGATIVE = "B-", "B-"
        AB_POSITIVE = "AB+", "AB+"
        AB_NEGATIVE = "AB-", "AB-"
        O_POSITIVE = "O+", "O+"
        O_NEGATIVE = "O-", "O-"
        UNKNOWN = "UNK", "Unknown"

    blood_type = models.CharField(
        max_length=3, choices=BloodType.choices, default=BloodType.UNKNOWN, blank=True
    )
    medical_condition = models.TextField(
        blank=True, help_text="A summary of the patient's current medical condition."
    )
    date_of_admission = models.DateField(null=True, blank=True)
    discharge_date = models.DateField(null=True, blank=True)
    assigned_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients",
        limit_choices_to={"role": User.Role.DOCTOR},
        help_text="The primary doctor assigned to this patient.",
    )
    medication = models.TextField(blank=True, help_text="List of prescribed medications.")
    test_results = models.TextField(blank=True, help_text="Summary of recent test results.")
    
    # Additional fields from CSV data
    hospital = models.CharField(max_length=255, blank=True, help_text="Hospital or medical facility name.")
    insurance_provider = models.CharField(max_length=255, blank=True, help_text="Patient's insurance provider.")
    billing_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Billing amount for treatment.")
    room_number = models.CharField(max_length=20, blank=True, help_text="Hospital room number.")
    admission_type = models.CharField(max_length=50, blank=True, help_text="Type of admission (emergency, scheduled, etc.).")

    class Meta:
        db_table = "patient_profiles"
        verbose_name = "Patient Profile"
        verbose_name_plural = "Patient Profiles"

    def __str__(self):
        return f"Patient {self.user.full_name}"