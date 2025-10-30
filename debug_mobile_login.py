#!/usr/bin/env python3
"""
Debug Mobile Login Connectivity
Tests all mobile endpoints and authentication flows to identify login issues
"""

import requests
import json
import time
from typing import Dict, Any, List

# Mobile endpoints to test (matching the frontend configuration)
MOBILE_ENDPOINTS = [
    "http://172.20.29.202:8000/api",
    "http://10.0.2.2:8000/api",
    "http://192.168.55.101:8000/api",
    "http://192.168.1.100:8000/api", 
    "http://localhost:8000/api",
    "http://127.0.0.1:8000/api"
]

# Test credentials
TEST_CREDENTIALS = {
    "email": "test@example.com",
    "password": "testpassword123"
}

def test_endpoint_connectivity(endpoint: str) -> Dict[str, Any]:
    """Test basic connectivity to an endpoint"""
    print(f"\n🔍 Testing connectivity: {endpoint}")
    
    try:
        start_time = time.time()
        response = requests.get(
            f"{endpoint}/users/profile/",
            timeout=5,
            headers={'Accept': 'application/json'}
        )
        response_time = (time.time() - start_time) * 1000
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Time: {response_time:.0f}ms")
        
        if response.status_code < 500:
            print(f"  ✅ SUCCESS - Endpoint is accessible")
            return {
                "success": True,
                "status_code": response.status_code,
                "response_time": response_time,
                "error": None
            }
        else:
            print(f"  ❌ FAILED - Server error: {response.status_code}")
            return {
                "success": False,
                "status_code": response.status_code,
                "response_time": response_time,
                "error": f"Server error: {response.status_code}"
            }
            
    except requests.exceptions.ConnectTimeout:
        print(f"  ❌ FAILED - Connection timeout")
        return {
            "success": False,
            "status_code": None,
            "response_time": None,
            "error": "Connection timeout"
        }
    except requests.exceptions.ConnectionError as e:
        print(f"  ❌ FAILED - Connection error: {str(e)}")
        return {
            "success": False,
            "status_code": None,
            "response_time": None,
            "error": f"Connection error: {str(e)}"
        }
    except Exception as e:
        print(f"  ❌ FAILED - Unexpected error: {str(e)}")
        return {
            "success": False,
            "status_code": None,
            "response_time": None,
            "error": f"Unexpected error: {str(e)}"
        }

def test_login_endpoint(endpoint: str) -> Dict[str, Any]:
    """Test login functionality on an endpoint"""
    print(f"\n🔐 Testing login: {endpoint}/users/login/")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{endpoint}/users/login/",
            json=TEST_CREDENTIALS,
            timeout=10,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        response_time = (time.time() - start_time) * 1000
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Time: {response_time:.0f}ms")
        
        try:
            response_data = response.json()
            print(f"  Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"  Response Text: {response.text[:200]}...")
        
        # For login, we expect either success (200) or authentication failure (400/401)
        if response.status_code in [200, 400, 401]:
            print(f"  ✅ SUCCESS - Login endpoint is accessible")
            return {
                "success": True,
                "status_code": response.status_code,
                "response_time": response_time,
                "error": None
            }
        else:
            print(f"  ❌ FAILED - Unexpected status: {response.status_code}")
            return {
                "success": False,
                "status_code": response.status_code,
                "response_time": response_time,
                "error": f"Unexpected status: {response.status_code}"
            }
            
    except Exception as e:
        print(f"  ❌ FAILED - Error: {str(e)}")
        return {
            "success": False,
            "status_code": None,
            "response_time": None,
            "error": str(e)
        }

def main():
    print("🔍 Mobile Login Debug Tool")
    print("=" * 50)
    
    connectivity_results = []
    login_results = []
    
    # Test connectivity to all endpoints
    print("\n📡 CONNECTIVITY TESTS")
    print("-" * 30)
    for endpoint in MOBILE_ENDPOINTS:
        result = test_endpoint_connectivity(endpoint)
        result['endpoint'] = endpoint
        connectivity_results.append(result)
    
    # Test login on accessible endpoints
    print("\n🔐 LOGIN TESTS")
    print("-" * 30)
    accessible_endpoints = [r for r in connectivity_results if r['success']]
    
    if not accessible_endpoints:
        print("❌ No accessible endpoints found for login testing")
    else:
        for result in accessible_endpoints:
            login_result = test_login_endpoint(result['endpoint'])
            login_result['endpoint'] = result['endpoint']
            login_results.append(login_result)
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 50)
    
    print(f"\n🌐 Connectivity Results:")
    for result in connectivity_results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        error_info = f" - {result['error']}" if result['error'] else ""
        print(f"  {status} - {result['endpoint']}{error_info}")
    
    if login_results:
        print(f"\n🔐 Login Results:")
        for result in login_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            error_info = f" - {result['error']}" if result['error'] else ""
            print(f"  {status} - {result['endpoint']}{error_info}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    working_endpoints = [r for r in connectivity_results if r['success']]
    
    if working_endpoints:
        best_endpoint = min(working_endpoints, key=lambda x: x['response_time'] or float('inf'))
        print(f"  🎯 Best endpoint: {best_endpoint['endpoint']} ({best_endpoint['response_time']:.0f}ms)")
        print(f"  📱 Mobile app should use: {best_endpoint['endpoint']}")
    else:
        print(f"  ⚠️  No working endpoints found!")
        print(f"  🔧 Check if Django server is running on 0.0.0.0:8000")
        print(f"  🔧 Verify ALLOWED_HOSTS includes mobile IPs")
        print(f"  🔧 Check network connectivity between mobile device and server")

if __name__ == "__main__":
    main()