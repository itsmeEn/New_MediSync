import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.users.models import GeneralDoctorProfile

qs = GeneralDoctorProfile.objects.filter(
    user__verification_status='approved',
    user__is_active=True,
    available_for_consultation=True,
)

blank_count = qs.filter(specialization__isnull=True).count() + qs.filter(specialization='').count()
nonblank_count = qs.exclude(specialization__isnull=True).exclude(specialization='').count()

print('Approved & active & available doctors:', qs.count())
print(' - blank specialization:', blank_count)
print(' - non-blank specialization:', nonblank_count)

# Sample of up to 5 doctors with blank specialization
for d in qs.filter(specialization__isnull=True)[:5]:
    print(f"BlankSpec Doctor: {d.user.full_name} | Hospital: {getattr(d.user, 'hospital_name', '')}")
for d in qs.filter(specialization='')[:5]:
    print(f"EmptySpec Doctor: {d.user.full_name} | Hospital: {getattr(d.user, 'hospital_name', '')}")