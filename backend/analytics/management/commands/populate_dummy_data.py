from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

from backend.users.models import PatientProfile, GeneralDoctorProfile, NurseProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with dummy data for analytics testing (does not interfere with normal user accounts)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of dummy records to create (default: 50)'
        )
        parser.add_argument(
            '--clear-dummy',
            action='store_true',
            help='Clear only dummy data before populating (keeps normal users)'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear_dummy = options['clear_dummy']
        
        if clear_dummy:
            self.stdout.write('Clearing only dummy data (keeping normal users)...')
            # Only delete dummy data (users with email containing 'dummy' or specific pattern)
            dummy_users = User.objects.filter(email__contains='dummy')
            dummy_count = dummy_users.count()
            dummy_users.delete()
            self.stdout.write(f'Cleared {dummy_count} dummy user records.')
        
        self.stdout.write(f'Creating {count} dummy patient records for analytics testing...')
        
        # Create dummy data
        self.create_dummy_data(count)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} dummy patient records for analytics!')
        )

    def create_dummy_data(self, count):
        """Create comprehensive dummy data for testing"""
        
        # Sample data for realistic testing
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jessica',
            'William', 'Ashley', 'James', 'Amanda', 'Christopher', 'Jennifer', 'Daniel',
            'Lisa', 'Michelle', 'Anthony', 'Kimberly', 'Mark', 'Donna',
            'Donald', 'Carol', 'Steven', 'Sandra', 'Paul', 'Ruth', 'Andrew', 'Sharon'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin'
        ]
        
        genders = ['Male', 'Female', 'Other']
        
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        medical_conditions = [
            'Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 'Heart Disease',
            'Depression', 'Anxiety', 'Migraine', 'Allergies', 'Obesity',
            'High Cholesterol', 'Sleep Apnea', 'COPD', 'Cancer', 'Stroke',
            'Kidney Disease', 'Liver Disease', 'Thyroid Disorder', 'Epilepsy',
            'Pneumonia', 'Bronchitis', 'Sinusitis', 'Gastritis', 'Ulcer'
        ]
        
        doctors = [
            'Dr. Sarah Johnson', 'Dr. Michael Chen', 'Dr. Emily Rodriguez',
            'Dr. David Kim', 'Dr. Lisa Thompson', 'Dr. Robert Wilson',
            'Dr. Jennifer Davis', 'Dr. Christopher Brown', 'Dr. Amanda Taylor',
            'Dr. Daniel Martinez'
        ]
        
        hospitals = [
            'General Hospital', 'City Medical Center', 'Regional Health System',
            'University Medical Center', 'Community Hospital', 'Metropolitan Health',
            'Central Medical', 'Valley Hospital', 'Riverside Medical',
            'Mountain View Hospital'
        ]
        
        insurance_providers = [
            'Blue Cross Blue Shield', 'Aetna', 'Cigna', 'UnitedHealth',
            'Humana', 'Kaiser Permanente', 'Anthem', 'Molina Healthcare',
            'Centene', 'WellCare'
        ]
        
        admission_types = [
            'Emergency', 'Scheduled', 'Urgent', 'Routine', 'Observation',
            'Outpatient', 'Inpatient', 'Day Surgery'
        ]
        
        medications = [
            'Lisinopril', 'Metformin', 'Atorvastatin', 'Amlodipine', 'Omeprazole',
            'Losartan', 'Albuterol', 'Gabapentin', 'Tramadol', 'Hydrochlorothiazide',
            'Sertraline', 'Metoprolol', 'Simvastatin', 'Furosemide', 'Warfarin',
            'Prednisone', 'Lorazepam', 'Oxycodone', 'Ibuprofen', 'Acetaminophen'
        ]
        
        test_results = [
            'Normal', 'Abnormal', 'Pending', 'Positive', 'Negative',
            'Elevated', 'Low', 'High', 'Borderline', 'Inconclusive'
        ]
        
        departments = [
            'Emergency', 'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics',
            'Oncology', 'Radiology', 'Surgery', 'Internal Medicine', 'Psychiatry'
        ]
        
        specializations = [
            'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Oncology',
            'Radiology', 'Surgery', 'Internal Medicine', 'Psychiatry', 'Dermatology'
        ]
        
        # Create users and patient profiles
        for i in range(count):
            try:
                # Generate random data
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                gender = random.choice(genders)
                blood_type = random.choice(blood_types)
                medical_condition = random.choice(medical_conditions)
                doctor = random.choice(doctors)
                hospital = random.choice(hospitals)
                insurance = random.choice(insurance_providers)
                admission_type = random.choice(admission_types)
                medication = random.choice(medications)
                test_result = random.choice(test_results)
                
                # Generate age (18-80)
                age = random.randint(18, 80)
                
                # Generate billing amount (100-50000)
                billing_amount = round(random.uniform(100, 50000), 2)
                
                # Generate room number (100-999)
                room_number = random.randint(100, 999)
                
                # Generate dates
                admission_date = timezone.now() - timedelta(days=random.randint(1, 365))
                discharge_date = admission_date + timedelta(days=random.randint(1, 30))
                
                # Create user with dummy namespace
                email = f"dummy.{first_name.lower()}{last_name.lower()}{i}@example.com"
                
                user = User.objects.create_user(
                    email=email,
                    password='testpass123',
                    first_name=first_name,
                    last_name=last_name,
                    full_name=f"{first_name} {last_name}",
                    role='patient',
                    date_of_birth=timezone.now().date() - timedelta(days=age*365),
                    gender=gender,
                    is_active=True,
                    is_verified=True
                )
                
                # Create patient profile with only existing fields
                patient_profile = PatientProfile.objects.create(
                    user=user,
                    blood_type=blood_type,
                    medical_condition=medical_condition,
                    date_of_admission=admission_date,
                    discharge_date=discharge_date,
                    hospital=hospital,
                    insurance_provider=insurance,
                    billing_amount=billing_amount,
                    room_number=str(room_number),
                    admission_type=admission_type,
                    medication=medication,
                    test_results=test_result
                )
                
                # Create some doctor and nurse profiles for testing
                if i < 10:  # Create 10 doctors
                    doctor_user = User.objects.create_user(
                        email=f"dummy.doctor{i}@example.com",
                        password='testpass123',
                        first_name=f"Dr. {first_name}",
                        last_name=last_name,
                        full_name=f"Dr. {first_name} {last_name}",
                        role='doctor',
                        is_active=True,
                        is_verified=True
                    )
                    
                    GeneralDoctorProfile.objects.create(
                        user=doctor_user,
                        specialization=random.choice(specializations),
                        license_number=f"MD{random.randint(100000, 999999)}"
                    )
                
                if i < 5:  # Create 5 nurses
                    nurse_user = User.objects.create_user(
                        email=f"dummy.nurse{i}@example.com",
                        password='testpass123',
                        first_name=f"Nurse {first_name}",
                        last_name=last_name,
                        full_name=f"Nurse {first_name} {last_name}",
                        role='nurse',
                        is_active=True,
                        is_verified=True
                    )
                    
                    NurseProfile.objects.create(
                        user=nurse_user,
                        department=random.choice(departments),
                        license_number=f"RN{random.randint(100000, 999999)}"
                    )
                
                if i % 10 == 0:
                    self.stdout.write(f'Created {i+1} records...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating record {i}: {str(e)}')
                )
                continue
        
        self.stdout.write('Dummy data creation completed!')