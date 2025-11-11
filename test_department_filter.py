import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.users.models import User, GeneralDoctorProfile

# Test different department filter scenarios
doctor_user = User.objects.get(email='eucliffeplays@gmail.com')
print('Doctor Hospital Name:', doctor_user.hospital_name)

# Test what happens with different department values
test_departments = ['General Medicine', 'general-medicine', 'Baseco Public Hospital', 'baseco']

for dept in test_departments:
    doctors = GeneralDoctorProfile.objects.filter(
        user__verification_status='approved',
        user__is_active=True,
        available_for_consultation=True,
        user__hospital_name__icontains=dept
    ).select_related('user')
    
    print(f'Department filter "{dept}": {doctors.count()} doctors found')
    for doctor in doctors:
        print(f'  - {doctor.user.full_name} at {doctor.user.hospital_name}')