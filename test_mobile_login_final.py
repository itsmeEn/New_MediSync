#!/usr/bin/env python3
"""
Final Mobile Login Test Script
Tests the mobile login functionality after applying all network configuration fixes.
"""

import requests
import json
import time
from typing import Dict, List, Tuple

# Updated mobile endpoints with the correct network IP
MOBILE_ENDPOINTS = [
    "http://172.20.29.202:8000/api",  # Current network IP (primary)
    "http://127.0.0.1:8000/api",      # Localhost (fallback)
    "http://10.0.2.2:8000/api",       # Android emulator host
]

# Test credentials (these should fail with 401, which is expected)
TEST_CREDENTIALS = {
    "email": "test@example.com",
    "password": "testpassword123"
}

def test_endpoint_connectivity(endpoint: str) -> Tuple[bool, Dict]:
    """Test basic connectivity to an endpoint."""
    try:
        start_time = time.time()
        response = requests.get(f"{endpoint}/users/profile/", timeout=5)
        response_time = int((time.time() - start_time) * 1000)
        
        return True, {
            "status_code": response.status_code,
            "response_time": response_time,
            "accessible": True
        }
    except requests.exceptions.RequestException as e:
        return False, {
            "error": str(e),
            "accessible": False
        }

def test_login_endpoint(endpoint: str) -> Tuple[bool, Dict]:
    """Test login functionality at an endpoint."""
    try:
        start_time = time.time()
        response = requests.post(
            f"{endpoint}/users/login/",
            json=TEST_CREDENTIALS,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response_time = int((time.time() - start_time) * 1000)
        
        # Parse response data
        try:
            response_data = response.json()
        except:
            response_data = {"raw_response": response.text}
        
        return True, {
            "status_code": response.status_code,
            "response_time": response_time,
            "response_data": response_data,
            "login_accessible": True
        }
    except requests.exceptions.RequestException as e:
        return False, {
            "error": str(e),
            "login_accessible": False
        }

def main():
    print("🔧 MOBILE LOGIN FINAL TEST")
    print("=" * 50)
    print(f"Testing {len(MOBILE_ENDPOINTS)} endpoints after configuration fixes...")
    print()
    
    connectivity_results = []
    login_results = []
    
    # Test connectivity
    print("🌐 CONNECTIVITY TESTS")
    print("-" * 30)
    for endpoint in MOBILE_ENDPOINTS:
        print(f"🔍 Testing: {endpoint}")
        success, result = test_endpoint_connectivity(endpoint)
        connectivity_results.append((endpoint, success, result))
        
        if success:
            print(f"  ✅ Status: {result['status_code']} | Time: {result['response_time']}ms")
        else:
            print(f"  ❌ Failed: {result['error'][:100]}...")
        print()
    
    # Test login functionality
    print("🔐 LOGIN FUNCTIONALITY TESTS")
    print("-" * 30)
    for endpoint in MOBILE_ENDPOINTS:
        print(f"🔐 Testing login: {endpoint}")
        success, result = test_login_endpoint(endpoint)
        login_results.append((endpoint, success, result))
        
        if success:
            print(f"  ✅ Status: {result['status_code']} | Time: {result['response_time']}ms")
            if result['status_code'] == 401:
                print(f"  ✅ Expected 401 response (invalid credentials)")
            print(f"  📄 Response: {json.dumps(result['response_data'], indent=2)}")
        else:
            print(f"  ❌ Failed: {result['error'][:100]}...")
        print()
    
    # Summary
    print("📊 FINAL SUMMARY")
    print("=" * 50)
    
    working_endpoints = []
    for endpoint, success, result in connectivity_results:
        if success and result.get('accessible'):
            working_endpoints.append(endpoint)
    
    working_login_endpoints = []
    for endpoint, success, result in login_results:
        if success and result.get('login_accessible'):
            working_login_endpoints.append(endpoint)
    
    print(f"🌐 Working Connectivity: {len(working_endpoints)}/{len(MOBILE_ENDPOINTS)}")
    for endpoint in working_endpoints:
        print(f"  ✅ {endpoint}")
    
    print(f"\n🔐 Working Login: {len(working_login_endpoints)}/{len(MOBILE_ENDPOINTS)}")
    for endpoint in working_login_endpoints:
        print(f"  ✅ {endpoint}")
    
    if working_login_endpoints:
        print(f"\n🎯 RECOMMENDED ENDPOINT: {working_login_endpoints[0]}")
        print("✅ Mobile login should now work correctly!")
        print("\n📱 NEXT STEPS:")
        print("1. Deploy the updated app to your Android device/emulator")
        print("2. Test login with valid credentials")
        print("3. The app should now successfully connect to the backend")
    else:
        print("\n❌ No working endpoints found. Please check:")
        print("1. Backend server is running on 0.0.0.0:8000")
        print("2. Network configuration is correct")
        print("3. Firewall settings allow connections")

if __name__ == "__main__":
    main()