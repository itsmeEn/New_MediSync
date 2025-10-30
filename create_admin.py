#!/usr/bin/env python
"""
Script to create or enforce a fixed admin user for the MediSync admin site.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from admin_site.models import AdminUser

def create_admin_user():
    """Create or update the fixed admin user without prompts."""
    # Fixed credentials as requested
    email = "admin@medisync.com"
    password = "Adminsh1!je590"
    full_name = "Admin"
    is_super_admin = True

    try:
        existing_admin = AdminUser.objects.filter(email=email).first()
        if existing_admin:
            # Update password and ensure verification/super admin flags
            existing_admin.set_password(password)
            existing_admin.full_name = full_name
            existing_admin.is_super_admin = is_super_admin
            existing_admin.is_email_verified = True
            existing_admin.save()
            print(f"Admin user enforced: {email}")
            return True

        # Create new fixed admin user
        admin = AdminUser.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            is_super_admin=is_super_admin,
            is_email_verified=True
        )
        print("Admin user created successfully!")
        print(f"Email: {admin.email}")
        print(f"Full Name: {admin.full_name}")
        print(f"Super Admin: {admin.is_super_admin}")
        print(f"User ID: {admin.id}")
        return True

    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False

if __name__ == "__main__":
    print("MediSync Admin User Enforcement")
    print("=" * 30)

    success = create_admin_user()

    if success:
        print("\nFixed admin credentials are now in place.")
        print("Login with:")
        print("  Email: admin@medisync.com")
        print("  Password: Adminsh1!je590")
    else:
        print("\nFailed to enforce admin user.")
