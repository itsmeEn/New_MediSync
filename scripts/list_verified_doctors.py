import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','backend.settings')
django.setup()
from backend.users.models import User, GeneralDoctorProfile

qs = User.objects.filter(role='doctor', is_verified=True)
print('Verified doctors:', qs.count())
for u in qs[:10]:
    print('Doctor:', u.id, u.full_name, '| Hospital:', u.hospital_name)

profiles = GeneralDoctorProfile.objects.filter(user__is_verified=True)
print('GeneralDoctorProfiles:', profiles.count())
for p in profiles[:10]:
    print('GeneralDoctor:', p.user.full_name, '| Hospital:', p.user.hospital_name, '| Spec:', p.specialization)