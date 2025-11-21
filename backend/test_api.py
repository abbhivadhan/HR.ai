#!/usr/bin/env python3
"""
Simple API test script to verify authentication endpoints.
Run this after starting the server to test the API.
"""

import requests
import json
import sys


def test_api_endpoints():
    """Test authentication API endpoints."""
    base_url = "http://localhost:8000/api"
    
    print("Testing authentication API endpoints...")
    
    # Test registration
    print("\n1. Testing user registration...")
    register_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "John",
        "last_name": "Doe",
        "user_type": "candidate"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", json=register_data)
        if response.status_code == 201:
            print("✓ Registration successful")
            user_data = response.json()
            print(f"  User ID: {user_data['id']}")
            print(f"  Email: {user_data['email']}")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
        return False
    
    # Test login
    print("\n2. Testing user login...")
    login_data = {
        "email": "test@example.com",
        "password": "TestPassword123"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    if response.status_code == 200:
        print("✓ Login successful")
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"  Token type: {token_data['token_type']}")
        print(f"  Expires in: {token_data['expires_in']} seconds")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False
    
    # Test protected endpoint
    print("\n3. Testing protected endpoint...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{base_url}/auth/me", headers=headers)
    
    if response.status_code == 200:
        print("✓ Protected endpoint access successful")
        user_info = response.json()
        print(f"  User: {user_info['first_name']} {user_info['last_name']}")
        print(f"  Email: {user_info['email']}")
        print(f"  Type: {user_info['user_type']}")
    else:
        print(f"❌ Protected endpoint failed: {response.status_code} - {response.text}")
        return False
    
    # Test invalid token
    print("\n4. Testing invalid token...")
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    response = requests.get(f"{base_url}/auth/me", headers=invalid_headers)
    
    if response.status_code == 401:
        print("✓ Invalid token correctly rejected")
    else:
        print(f"❌ Invalid token should be rejected: {response.status_code}")
        return False
    
    return True


def main():
    """Run API tests."""
    print("Authentication API Test Suite")
    print("=" * 40)
    
    if test_api_endpoints():
        print("\n🎉 All API tests passed!")
        return 0
    else:
        print("\n❌ Some API tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())