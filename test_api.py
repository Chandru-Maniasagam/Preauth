#!/usr/bin/env python3
"""
Simple test script to verify API endpoints
"""

import requests
import json

def test_api():
    base_url = "https://preauth-11.onrender.com"
    
    # Test headers
    headers = {
        "X-Hospital-ID": "HOSP_001",
        "X-User-ID": "test_user", 
        "X-User-Name": "Test User",
        "Content-Type": "application/json"
    }
    
    print("Testing API endpoints...")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing Health Check:")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Claims endpoint
    print("\n2. Testing Claims Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/v1/claims/", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Specialities endpoint
    print("\n3. Testing Specialities Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/v1/claims/specialities", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Doctors endpoint
    print("\n4. Testing Doctors Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/v1/claims/doctors", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Payers endpoint
    print("\n5. Testing Payers Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/v1/claims/payers", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
