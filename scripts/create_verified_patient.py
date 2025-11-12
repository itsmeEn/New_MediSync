#!/usr/bin/env python
import os
import sys
import argparse

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from backend.users.models import User, PatientProfile

parser = argparse.ArgumentParser(description='Create a verified patient user and output JWT tokens')
parser.add_argument('--email', type=str, required=True, help='Email address for the new patient')
parser.add_argument('--full-name', type=str, default='Test Patient', help='Full name')
parser.add_argument('--hospital', type=str, default='Baseco Public Hospital', help='Hospital name to assign')
args = parser.parse_args()

# Create or get user
user, created = User.objects.get_or_create(email=args.email, defaults={
    'full_name': args.full_name,
    'role': 'patient',
    'is_active': True,
})

# Ensure verified status
user.verification_status = 'approved'
user.is_verified = True
user.hospital_name = args.hospital
user.hospital_address = user.hospital_address or ''
user.date_joined = user.date_joined or timezone.now()
user.save()

# Ensure patient profile exists
profile, pcreated = PatientProfile.objects.get_or_create(user=user, defaults={
    'blood_type': 'UNK',
    'medical_condition': '',
})
profile.hospital = args.hospital
profile.save()

# Issue JWT tokens
refresh = RefreshToken.for_user(user)
access = str(refresh.access_token)
print('USER_ID=', user.id)
print('ACCESS_TOKEN=', access)
print('REFRESH_TOKEN=', str(refresh))
print('EMAIL=', user.email)
print('HOSPITAL=', args.hospital)