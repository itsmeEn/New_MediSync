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

from backend.users.models import User, PatientProfile

parser = argparse.ArgumentParser(description='Approve a user and optionally set hospital info')
parser.add_argument('--user-id', type=int, required=True, help='User ID to approve')
parser.add_argument('--status', type=str, default='approved', help='Verification status to set (default: approved)')
parser.add_argument('--hospital', type=str, default='', help='Hospital name to set on user and patient profile')
args = parser.parse_args()

user = User.objects.get(id=args.user_id)
user.verification_status = args.status
# Keep is_verified in sync when approved
if args.status.lower() == 'approved':
    user.is_verified = True
if args.hospital:
    user.hospital_name = args.hospital
    user.hospital_address = user.hospital_address or ''
user.save()

try:
    profile = PatientProfile.objects.get(user=user)
    if args.hospital:
        profile.hospital = args.hospital
        profile.save()
except PatientProfile.DoesNotExist:
    pass

print(f"User {user.id} ({user.email}) verification_status set to {user.verification_status}. is_verified={user.is_verified}. hospital={getattr(user, 'hospital_name', '')}")