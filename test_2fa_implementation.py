"""
Test script for Two-Factor Authentication (2FA) implementation
This script tests the complete 2FA flow for doctors and nurses
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def print_response(response, title="Response"):
    """Helper function to print formatted response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_2fa_flow():
    """Test the complete 2FA flow"""
    
    print("\n" + "="*60)
    print("TESTING TWO-FACTOR AUTHENTICATION (2FA) FLOW")
    print("="*60 + "\n")
    
    # Step 1: Register a test doctor (or use existing credentials)
    print("Step 1: Register a test doctor...")
    register_data = {
        "email": "doctor2fa@test.com",
        "full_name": "Dr. 2FA Test",
        "role": "doctor",
        "date_of_birth": "1985-05-15",
        "gender": "Male",
        "password": "Doctor123",
        "password2": "Doctor123",
        "license_number": "DOC2FA123",
        "specialization": "Cardiology"
    }
    
    register_response = requests.post(f"{BASE_URL}/api/users/register/", json=register_data)
    print_response(register_response, "Registration Response")
    
    # Get access token from registration or login
    if register_response.status_code == 201:
        access_token = register_response.json()['tokens']['access']
        print(f"✅ Registration successful. Access token obtained.")
    else:
        # Try to login with existing credentials
        print("Registration failed (user may already exist). Attempting login...")
        login_data = {
            "email": "doctor2fa@test.com",
            "password": "Doctor123"
        }
        login_response = requests.post(f"{BASE_URL}/api/users/login/", json=login_data)
        print_response(login_response, "Login Response")
        
        if login_response.status_code == 200:
            response_json = login_response.json()
            if 'requires_2fa' in response_json and response_json['requires_2fa']:
                print("\n⚠️ 2FA is already enabled for this user!")
                print("This test will demonstrate disabling and re-enabling 2FA.\n")
                
                # For testing purposes, we'll need to verify 2FA to get tokens
                print("Please enter the 6-digit OTP code from your authenticator app:")
                otp_code = input("OTP Code: ").strip()
                
                verify_login_data = {
                    "email": "doctor2fa@test.com",
                    "otp_code": otp_code
                }
                verify_response = requests.post(f"{BASE_URL}/api/users/2fa/login/verify/", json=verify_login_data)
                print_response(verify_response, "2FA Login Verification")
                
                if verify_response.status_code == 200:
                    access_token = verify_response.json()['access']
                else:
                    print("❌ 2FA verification failed. Cannot continue test.")
                    return
            else:
                access_token = response_json['access']
        else:
            print("❌ Login failed. Cannot continue test.")
            return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Enable 2FA
    print("\nStep 2: Enabling 2FA...")
    enable_response = requests.post(f"{BASE_URL}/api/users/2fa/enable/", headers=headers)
    print_response(enable_response, "Enable 2FA Response")
    
    if enable_response.status_code == 200:
        qr_code = enable_response.json().get('qr_code')
        secret = enable_response.json().get('secret')
        
        print(f"✅ 2FA setup initiated successfully!")
        print(f"\n📱 Secret Key: {secret}")
        print(f"\nInstructions:")
        print("1. Open your authenticator app (Google Authenticator, Authy, etc.)")
        print("2. Scan the QR code or manually enter the secret key above")
        print("3. Enter the 6-digit code from your app below to verify and activate 2FA\n")
        
        # Save QR code to file for easy scanning
        if qr_code:
            with open('2fa_qr_code.html', 'w') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>MediSync 2FA Setup</title>
                    <style>
                        body {{ 
                            font-family: Arial, sans-serif; 
                            text-align: center; 
                            padding: 50px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                        }}
                        .container {{
                            background: white;
                            border-radius: 15px;
                            padding: 40px;
                            max-width: 500px;
                            margin: 0 auto;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                            color: #333;
                        }}
                        h1 {{ color: #667eea; }}
                        img {{ 
                            border: 5px solid #667eea; 
                            border-radius: 10px; 
                            margin: 20px 0;
                        }}
                        .secret {{
                            background: #f0f0f0;
                            padding: 15px;
                            border-radius: 8px;
                            font-family: monospace;
                            font-size: 18px;
                            margin: 20px 0;
                            word-break: break-all;
                        }}
                        .instructions {{
                            text-align: left;
                            margin: 20px 0;
                            line-height: 1.8;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🔐 MediSync 2FA Setup</h1>
                        <p><strong>Scan this QR code with your authenticator app:</strong></p>
                        <img src="{qr_code}" alt="2FA QR Code" />
                        <p><strong>Or manually enter this secret key:</strong></p>
                        <div class="secret">{secret}</div>
                        <div class="instructions">
                            <h3>Instructions:</h3>
                            <ol>
                                <li>Open your authenticator app (Google Authenticator, Authy, Microsoft Authenticator, etc.)</li>
                                <li>Tap "Add account" or "+"</li>
                                <li>Choose "Scan QR code" and scan the code above</li>
                                <li>Or choose "Enter key manually" and type the secret key</li>
                                <li>Your app will generate a 6-digit code</li>
                                <li>Enter that code in the terminal to complete setup</li>
                            </ol>
                        </div>
                    </div>
                </body>
                </html>
                """)
            print("📄 QR code saved to '2fa_qr_code.html' - open it in your browser!")
        
        # Step 3: Verify and activate 2FA
        print("\nStep 3: Verifying OTP code...")
        otp_code = input("Enter the 6-digit code from your authenticator app: ").strip()
        
        verify_data = {
            "otp_code": otp_code
        }
        
        verify_response = requests.post(f"{BASE_URL}/api/users/2fa/verify/", json=verify_data, headers=headers)
        print_response(verify_response, "Verify 2FA Response")
        
        if verify_response.status_code == 200:
            print("✅ 2FA has been successfully enabled!")
            
            # Step 4: Test login with 2FA
            print("\nStep 4: Testing login with 2FA enabled...")
            login_data = {
                "email": "doctor2fa@test.com",
                "password": "Doctor123"
            }
            
            login_response = requests.post(f"{BASE_URL}/api/users/login/", json=login_data)
            print_response(login_response, "Login Response (with 2FA)")
            
            if login_response.json().get('requires_2fa'):
                print("✅ 2FA is working! Login requires OTP verification.")
                
                # Step 5: Verify OTP during login
                print("\nStep 5: Verifying OTP during login...")
                otp_code = input("Enter the 6-digit code from your authenticator app: ").strip()
                
                verify_login_data = {
                    "email": "doctor2fa@test.com",
                    "otp_code": otp_code
                }
                
                verify_login_response = requests.post(f"{BASE_URL}/api/users/2fa/login/verify/", json=verify_login_data)
                print_response(verify_login_response, "2FA Login Verification Response")
                
                if verify_login_response.status_code == 200:
                    print("✅ 2FA login verification successful!")
                    new_access_token = verify_login_response.json()['access']
                    
                    # Update headers with new token
                    headers = {
                        "Authorization": f"Bearer {new_access_token}",
                        "Content-Type": "application/json"
                    }
                    
                    # Step 6: Test disabling 2FA
                    print("\nStep 6: Testing 2FA disable functionality...")
                    password = input("Enter your password to disable 2FA: ").strip()
                    
                    disable_data = {
                        "password": password
                    }
                    
                    disable_response = requests.post(f"{BASE_URL}/api/users/2fa/disable/", json=disable_data, headers=headers)
                    print_response(disable_response, "Disable 2FA Response")
                    
                    if disable_response.status_code == 200:
                        print("✅ 2FA has been successfully disabled!")
                        print("\n🎉 All 2FA tests completed successfully!")
                    else:
                        print("❌ Failed to disable 2FA")
                else:
                    print("❌ 2FA login verification failed")
            else:
                print("❌ 2FA requirement not triggered during login")
        else:
            print("❌ Failed to verify and enable 2FA")
    else:
        print("❌ Failed to initiate 2FA setup")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

def test_nurse_2fa():
    """Test 2FA for a nurse account"""
    print("\n" + "="*60)
    print("TESTING 2FA FOR NURSE ACCOUNT")
    print("="*60 + "\n")
    
    # Register a test nurse
    register_data = {
        "email": "nurse2fa@test.com",
        "full_name": "Nurse 2FA Test",
        "role": "nurse",
        "date_of_birth": "1990-08-20",
        "gender": "Female",
        "password": "Nurse123",
        "password2": "Nurse123",
        "license_number": "NUR2FA123",
        "department": "Emergency"
    }
    
    register_response = requests.post(f"{BASE_URL}/api/users/register/", json=register_data)
    print_response(register_response, "Nurse Registration Response")
    
    if register_response.status_code == 201:
        access_token = register_response.json()['tokens']['access']
        print(f"✅ Nurse registration successful!")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Enable 2FA for nurse
        enable_response = requests.post(f"{BASE_URL}/api/users/2fa/enable/", headers=headers)
        print_response(enable_response, "Nurse Enable 2FA Response")
        
        if enable_response.status_code == 200:
            print("✅ 2FA setup initiated for nurse successfully!")
        else:
            print("❌ Failed to initiate 2FA for nurse")
    else:
        print("❌ Nurse registration failed (user may already exist)")

def test_patient_2fa_restriction():
    """Test that patients cannot enable 2FA"""
    print("\n" + "="*60)
    print("TESTING 2FA RESTRICTION FOR PATIENT")
    print("="*60 + "\n")
    
    # Register a test patient
    register_data = {
        "email": "patient2fa@test.com",
        "full_name": "Patient Test",
        "role": "patient",
        "date_of_birth": "1995-03-10",
        "gender": "Male",
        "password": "Patient123",
        "password2": "Patient123"
    }
    
    register_response = requests.post(f"{BASE_URL}/api/users/register/", json=register_data)
    print_response(register_response, "Patient Registration Response")
    
    if register_response.status_code == 201:
        access_token = register_response.json()['tokens']['access']
        print(f"✅ Patient registration successful!")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Try to enable 2FA for patient (should fail)
        enable_response = requests.post(f"{BASE_URL}/api/users/2fa/enable/", headers=headers)
        print_response(enable_response, "Patient Enable 2FA Response (Should Fail)")
        
        if enable_response.status_code == 403:
            print("✅ 2FA correctly restricted for patients!")
        else:
            print("❌ 2FA restriction not working properly for patients")
    else:
        print("❌ Patient registration failed (user may already exist)")

if __name__ == "__main__":
    import sys
    
    print("\n🔐 MediSync Two-Factor Authentication Test Suite 🔐\n")
    print("This script will test the complete 2FA implementation.")
    print("Make sure the Django server is running on http://localhost:8000\n")
    
    choice = input("Choose test:\n1. Full 2FA flow for doctor\n2. 2FA for nurse\n3. 2FA restriction for patient\n4. All tests\n\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        test_2fa_flow()
    elif choice == '2':
        test_nurse_2fa()
    elif choice == '3':
        test_patient_2fa_restriction()
    elif choice == '4':
        test_2fa_flow()
        test_nurse_2fa()
        test_patient_2fa_restriction()
    else:
        print("Invalid choice!")

