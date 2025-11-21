#!/usr/bin/env python3
"""
Simple test runner for the authentication system.
This script can be run without pytest to verify basic functionality.
"""

import sys
import os
import tempfile
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.database import Base
from app.models.user import User, UserType
from app.auth.utils import get_password_hash, verify_password, create_access_token, verify_token
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegistration, UserLogin


def test_password_utils():
    """Test password hashing utilities."""
    print("Testing password utilities...")
    
    password = "TestPassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password, "Password should be hashed"
    assert verify_password(password, hashed), "Password verification should work"
    assert not verify_password("wrong", hashed), "Wrong password should fail"
    
    print("✓ Password utilities working correctly")


def test_jwt_utils():
    """Test JWT token utilities."""
    print("Testing JWT utilities...")
    
    data = {"sub": "test-user-id", "email": "test@example.com"}
    token = create_access_token(data)
    
    assert token is not None, "Token should be created"
    assert isinstance(token, str), "Token should be a string"
    
    payload = verify_token(token)
    assert payload["sub"] == data["sub"], "Token should contain correct user ID"
    assert payload["email"] == data["email"], "Token should contain correct email"
    
    print("✓ JWT utilities working correctly")


def test_auth_service():
    """Test authentication service."""
    print("Testing authentication service...")
    
    # Create temporary database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    auth_service = AuthService(db)
    
    # Test user registration
    user_data = UserRegistration(
        email="test@example.com",
        password="TestPassword123",
        first_name="John",
        last_name="Doe",
        user_type=UserType.CANDIDATE
    )
    
    user = auth_service.register_user(user_data)
    assert user.email == "test@example.com", "User email should match"
    assert user.first_name == "John", "User first name should match"
    assert user.is_active, "User should be active"
    assert not user.is_verified, "User should not be verified initially"
    
    # Test authentication
    login_data = UserLogin(email="test@example.com", password="TestPassword123")
    authenticated_user = auth_service.authenticate_user(login_data)
    assert authenticated_user is not None, "Authentication should succeed"
    assert authenticated_user.id == user.id, "Authenticated user should match"
    
    # Test wrong password
    wrong_login = UserLogin(email="test@example.com", password="wrong")
    wrong_auth = auth_service.authenticate_user(wrong_login)
    assert wrong_auth is None, "Wrong password should fail"
    
    # Test token creation
    tokens = auth_service.create_tokens(user)
    assert "access_token" in tokens, "Should have access token"
    assert "refresh_token" in tokens, "Should have refresh token"
    assert tokens["token_type"] == "bearer", "Token type should be bearer"
    
    # Test email verification
    verification_success = auth_service.verify_email(user.verification_token)
    assert verification_success, "Email verification should succeed"
    
    db.refresh(user)
    assert user.is_verified, "User should be verified after verification"
    
    db.close()
    print("✓ Authentication service working correctly")


def main():
    """Run all tests."""
    print("Running authentication system tests...\n")
    
    try:
        test_password_utils()
        test_jwt_utils()
        test_auth_service()
        
        print("\n🎉 All tests passed! Authentication system is working correctly.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())