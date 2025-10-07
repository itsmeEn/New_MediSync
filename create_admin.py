#!/usr/bin/env python
"""
Script to create an admin user for the MediSync admin site.
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
    """Create an admin user for the admin site."""
    
    email = input("Enter admin email (default: admin@medisync.com): ").strip()
    if not email:
        email = "admin@medisync.com"
    
    password = input("Enter admin password (default: admin123456): ").strip()
    if not password:
        password = "admin123456"
    
    full_name = input("Enter admin full name (default: Admin User): ").strip()
    if not full_name:
        full_name = "Admin User"
    
    is_super_admin = input("Is this a super admin? (y/n, default: y): ").strip().lower()
    is_super_admin = is_super_admin != 'n'
    
    try:
        # Check if admin user already exists
        existing_admin = AdminUser.objects.filter(email=email).first()
        if existing_admin:
            print(f"Admin user with email {email} already exists.")
            update = input("Do you want to update the password? (y/n): ").strip().lower()
            if update == 'y':
                existing_admin.set_password(password)
                existing_admin.full_name = full_name
                existing_admin.is_super_admin = is_super_admin
                existing_admin.save()
                print(f"Admin user updated: {email}")
            return
        
        # Create new admin user
        admin = AdminUser.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            is_super_admin=is_super_admin,
            is_email_verified=True  # Set as verified for default admin
        )
        
        print(f"Admin user created successfully!")
        print(f"Email: {admin.email}")
        print(f"Full Name: {admin.full_name}")
        print(f"Super Admin: {admin.is_super_admin}")
        print(f"User ID: {admin.id}")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("MediSync Admin User Creation")
    print("=" * 30)
    
    success = create_admin_user()
    
    if success:
        print("\nAdmin user created successfully!")
        print("You can now login to the admin dashboard.")
    else:
        print("\nFailed to create admin user.")
        sys.exit(1)
