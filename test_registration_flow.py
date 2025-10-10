#!/usr/bin/env python3
"""
Test script to verify registration flow and error handling
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_duplicate_email_registration():
    """Test registration with duplicate email"""
    print("Testing duplicate email registration...")
    
    # First, try to register with an existing email
    registration_data = {
        "email": "euniceibardalozad@gmail.com",
        "full_name": "Test User",
        "password": "testpassword123",
        "password2": "testpassword123",
        "date_of_birth": "1990-01-01",
        "gender": "Female",
        "role": "doctor",
        "license_number": "TEST123",
        "specialization": "General Medicine"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/users/register/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            response_data = response.json()
            if "email" in response_data and "already exists" in str(response_data["email"]):
                print("✅ Duplicate email validation working correctly!")
                return True
            else:
                print("❌ Duplicate email validation not working as expected")
                return False
        else:
            print("❌ Expected 400 status code for duplicate email")
            return False
            
    except Exception as e:
        print(f"❌ Error during registration test: {e}")
        return False

def test_new_user_registration():
    """Test registration with new email"""
    print("\nTesting new user registration...")
    
    # Try to register with a new email
    registration_data = {
        "email": "newuser@test.com",
        "full_name": "New Test User",
        "password": "testpassword123",
        "password2": "testpassword123",
        "date_of_birth": "1990-01-01",
        "gender": "Male",
        "role": "nurse",
        "license_number": "NURSE123",
        "department": "Emergency"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/users/register/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ New user registration working correctly!")
            return True
        elif response.status_code == 400:
            response_data = response.json()
            if "email" in response_data and "already exists" in str(response_data["email"]):
                print("✅ User already exists (expected if run multiple times)")
                return True
            else:
                print(f"❌ Registration failed with validation errors: {response_data}")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during registration test: {e}")
        return False

def test_login_flow():
    """Test login with existing user"""
    print("\nTesting login flow...")
    
    # Try different possible passwords
    passwords_to_try = ["Eunice123", "eunice123", "password123", "testpassword123"]
    
    for password in passwords_to_try:
        print(f"Trying password: {password}")
        login_data = {
            "email": "euniceibardalozad@gmail.com",
            "password": password
        }
    
    try:
        response = requests.post(f"{BASE_URL}/api/users/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            if "access" in response_data and "refresh" in response_data:
                print("✅ Login working correctly!")
                return True
            else:
                print("❌ Login response missing tokens")
                return False
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing MediSync Registration and Login Flow")
    print("=" * 50)
    
    # Test duplicate email registration
    duplicate_test = test_duplicate_email_registration()
    
    # Test new user registration
    new_user_test = test_new_user_registration()
    
    # Test login flow
    login_test = test_login_flow()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Duplicate Email Validation: {'✅ PASS' if duplicate_test else '❌ FAIL'}")
    print(f"New User Registration: {'✅ PASS' if new_user_test else '❌ FAIL'}")
    print(f"Login Flow: {'✅ PASS' if login_test else '❌ FAIL'}")
    
    if all([duplicate_test, new_user_test, login_test]):
        print("\n🎉 All tests passed! Registration and login flow working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")