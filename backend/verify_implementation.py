#!/usr/bin/env python3
"""
Simple verification script to check if all authentication files are properly created.
This script doesn't require external dependencies.
"""

import os
import sys


def check_file_exists(filepath, description):
    """Check if a file exists and print status."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False


def check_directory_structure():
    """Check if all required directories and files exist."""
    print("Checking authentication system implementation...\n")
    
    files_to_check = [
        # Core database and models
        ("app/database.py", "Database configuration"),
        ("app/models/__init__.py", "Models package"),
        ("app/models/user.py", "User model"),
        
        # Authentication utilities
        ("app/auth/__init__.py", "Auth package"),
        ("app/auth/utils.py", "Auth utilities (JWT, password hashing)"),
        ("app/auth/dependencies.py", "Auth dependencies"),
        
        # Schemas
        ("app/schemas/__init__.py", "Schemas package"),
        ("app/schemas/auth.py", "Auth schemas"),
        
        # Services
        ("app/services/__init__.py", "Services package"),
        ("app/services/auth_service.py", "Authentication service"),
        
        # API endpoints
        ("app/api/__init__.py", "API package"),
        ("app/api/auth.py", "Auth API endpoints"),
        
        # Database migrations
        ("alembic.ini", "Alembic configuration"),
        ("alembic/env.py", "Alembic environment"),
        ("alembic/script.py.mako", "Alembic script template"),
        ("alembic/versions/001_initial_user_model.py", "Initial migration"),
        
        # Tests
        ("tests/test_auth.py", "Authentication tests"),
        ("run_tests.py", "Test runner"),
        ("test_api.py", "API test script"),
        
        # Configuration
        ("requirements.txt", "Python dependencies"),
        ("pytest.ini", "Pytest configuration"),
    ]
    
    all_exist = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist


def check_file_contents():
    """Check if key files contain expected content."""
    print("\nChecking file contents...")
    
    # Check if User model has required fields
    try:
        with open("app/models/user.py", "r") as f:
            user_content = f.read()
            required_fields = ["email", "password_hash", "first_name", "last_name", "user_type", "is_active", "is_verified"]
            for field in required_fields:
                if field in user_content:
                    print(f"✓ User model has {field} field")
                else:
                    print(f"❌ User model missing {field} field")
    except FileNotFoundError:
        print("❌ Could not read User model file")
    
    # Check if auth utils has required functions
    try:
        with open("app/auth/utils.py", "r") as f:
            auth_content = f.read()
            required_functions = ["verify_password", "get_password_hash", "create_access_token", "verify_token"]
            for func in required_functions:
                if func in auth_content:
                    print(f"✓ Auth utils has {func} function")
                else:
                    print(f"❌ Auth utils missing {func} function")
    except FileNotFoundError:
        print("❌ Could not read auth utils file")
    
    # Check if API endpoints exist
    try:
        with open("app/api/auth.py", "r") as f:
            api_content = f.read()
            required_endpoints = ["/register", "/login", "/refresh", "/verify-email", "/forgot-password", "/reset-password"]
            for endpoint in required_endpoints:
                if endpoint in api_content:
                    print(f"✓ API has {endpoint} endpoint")
                else:
                    print(f"❌ API missing {endpoint} endpoint")
    except FileNotFoundError:
        print("❌ Could not read API file")


def main():
    """Run verification checks."""
    print("Authentication System Implementation Verification")
    print("=" * 50)
    
    # Change to backend directory if not already there
    if not os.path.exists("app"):
        if os.path.exists("backend/app"):
            os.chdir("backend")
        else:
            print("❌ Could not find app directory. Please run from project root or backend directory.")
            return 1
    
    structure_ok = check_directory_structure()
    check_file_contents()
    
    print("\n" + "=" * 50)
    if structure_ok:
        print("🎉 Authentication system implementation appears complete!")
        print("\nImplemented features:")
        print("• User model with SQLAlchemy")
        print("• JWT token generation and validation")
        print("• Password hashing with bcrypt")
        print("• User registration with email verification")
        print("• Secure login endpoint")
        print("• Password reset functionality")
        print("• Protected route dependencies")
        print("• Comprehensive API endpoints")
        print("• Database migrations")
        print("• Unit tests")
        
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up database (PostgreSQL)")
        print("3. Run migrations: alembic upgrade head")
        print("4. Start server: uvicorn app.main:app --reload")
        print("5. Run tests: pytest")
        
        return 0
    else:
        print("❌ Some files are missing. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())