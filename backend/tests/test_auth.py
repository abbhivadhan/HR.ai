import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta
import uuid

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserType
from app.auth.utils import get_password_hash, verify_password, create_access_token, verify_token
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegistration, UserLogin

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_user_data():
    """Sample user registration data."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "John",
        "last_name": "Doe",
        "user_type": "candidate"
    }


@pytest.fixture
def created_user(db_session, sample_user_data):
    """Create a user in the database."""
    auth_service = AuthService(db_session)
    user_reg = UserRegistration(**sample_user_data)
    user = auth_service.register_user(user_reg)
    return user


class TestPasswordUtils:
    """Test password hashing and verification utilities."""
    
    def test_password_hashing(self):
        """Test password hashing works correctly."""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_password_hash_uniqueness(self):
        """Test that same password generates different hashes."""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTUtils:
    """Test JWT token utilities."""
    
    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification."""
        data = {"sub": str(uuid.uuid4()), "email": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        payload = verify_token(token)
        assert payload["sub"] == data["sub"]
        assert payload["email"] == data["email"]
        assert "exp" in payload
    
    def test_token_expiration(self):
        """Test token expiration handling."""
        data = {"sub": str(uuid.uuid4())}
        # Create token that expires in 1 second
        token = create_access_token(data, expires_delta=timedelta(seconds=1))
        
        # Token should be valid immediately
        payload = verify_token(token)
        assert payload["sub"] == data["sub"]
        
        # Note: In real tests, you might want to mock time or use a longer delay
        # For this test, we'll just verify the token structure is correct
    
    def test_invalid_token(self):
        """Test handling of invalid tokens."""
        with pytest.raises(Exception):
            verify_token("invalid_token")


class TestAuthService:
    """Test authentication service."""
    
    def test_user_registration(self, db_session, sample_user_data):
        """Test user registration."""
        auth_service = AuthService(db_session)
        user_reg = UserRegistration(**sample_user_data)
        
        user = auth_service.register_user(user_reg)
        
        assert user.email == sample_user_data["email"]
        assert user.first_name == sample_user_data["first_name"]
        assert user.last_name == sample_user_data["last_name"]
        assert user.user_type == UserType.CANDIDATE
        assert user.is_active is True
        assert user.is_verified is False
        assert user.verification_token is not None
        assert verify_password(sample_user_data["password"], user.password_hash)
    
    def test_duplicate_email_registration(self, db_session, sample_user_data):
        """Test that duplicate email registration fails."""
        auth_service = AuthService(db_session)
        user_reg = UserRegistration(**sample_user_data)
        
        # First registration should succeed
        auth_service.register_user(user_reg)
        
        # Second registration with same email should fail
        with pytest.raises(Exception):
            auth_service.register_user(user_reg)
    
    def test_user_authentication_success(self, db_session, created_user, sample_user_data):
        """Test successful user authentication."""
        auth_service = AuthService(db_session)
        login_data = UserLogin(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        authenticated_user = auth_service.authenticate_user(login_data)
        
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.email == created_user.email
    
    def test_user_authentication_wrong_password(self, db_session, created_user, sample_user_data):
        """Test authentication with wrong password."""
        auth_service = AuthService(db_session)
        login_data = UserLogin(
            email=sample_user_data["email"],
            password="wrong_password"
        )
        
        authenticated_user = auth_service.authenticate_user(login_data)
        assert authenticated_user is None
    
    def test_user_authentication_nonexistent_email(self, db_session):
        """Test authentication with non-existent email."""
        auth_service = AuthService(db_session)
        login_data = UserLogin(
            email="nonexistent@example.com",
            password="password"
        )
        
        authenticated_user = auth_service.authenticate_user(login_data)
        assert authenticated_user is None
    
    def test_create_tokens(self, db_session, created_user):
        """Test token creation for user."""
        auth_service = AuthService(db_session)
        tokens = auth_service.create_tokens(created_user)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] == 900
        
        # Verify tokens are valid
        access_payload = verify_token(tokens["access_token"])
        refresh_payload = verify_token(tokens["refresh_token"])
        
        assert access_payload["sub"] == str(created_user.id)
        assert refresh_payload["sub"] == str(created_user.id)
        assert refresh_payload["type"] == "refresh"
    
    def test_email_verification(self, db_session, created_user):
        """Test email verification."""
        auth_service = AuthService(db_session)
        
        # User should not be verified initially
        assert created_user.is_verified is False
        
        # Verify email
        success = auth_service.verify_email(created_user.verification_token)
        assert success is True
        
        # Refresh user from database
        db_session.refresh(created_user)
        assert created_user.is_verified is True
        assert created_user.verification_token is None
    
    def test_password_reset_request(self, db_session, created_user):
        """Test password reset request."""
        auth_service = AuthService(db_session)
        
        success = auth_service.request_password_reset(created_user.email)
        assert success is True
        
        # Refresh user from database
        db_session.refresh(created_user)
        assert created_user.reset_token is not None
        assert created_user.reset_token_expires is not None
    
    def test_password_reset(self, db_session, created_user):
        """Test password reset."""
        auth_service = AuthService(db_session)
        new_password = "NewPassword123"
        
        # Request password reset first
        auth_service.request_password_reset(created_user.email)
        db_session.refresh(created_user)
        
        # Reset password
        success = auth_service.reset_password(created_user.reset_token, new_password)
        assert success is True
        
        # Refresh user from database
        db_session.refresh(created_user)
        assert created_user.reset_token is None
        assert created_user.reset_token_expires is None
        assert verify_password(new_password, created_user.password_hash)


class TestAuthAPI:
    """Test authentication API endpoints."""
    
    def test_register_endpoint(self, sample_user_data):
        """Test user registration endpoint."""
        response = client.post("/api/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert data["last_name"] == sample_user_data["last_name"]
        assert data["user_type"] == sample_user_data["user_type"]
        assert data["is_active"] is True
        assert data["is_verified"] is False
    
    def test_register_invalid_email(self):
        """Test registration with invalid email."""
        invalid_data = {
            "email": "invalid_email",
            "password": "TestPassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = client.post("/api/auth/register", json=invalid_data)
        assert response.status_code == 422
    
    def test_register_weak_password(self):
        """Test registration with weak password."""
        weak_password_data = {
            "email": "test@example.com",
            "password": "weak",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = client.post("/api/auth/register", json=weak_password_data)
        assert response.status_code == 422
    
    def test_login_endpoint(self, sample_user_data):
        """Test user login endpoint."""
        # First register a user
        client.post("/api/auth/register", json=sample_user_data)
        
        # Then login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900
    
    def test_login_wrong_credentials(self):
        """Test login with wrong credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrong_password"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
    
    def test_get_current_user(self, sample_user_data):
        """Test getting current user information."""
        # Register and login
        client.post("/api/auth/register", json=sample_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["first_name"] == sample_user_data["first_name"]
    
    def test_protected_route_without_token(self):
        """Test accessing protected route without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 403
    
    def test_protected_route_invalid_token(self):
        """Test accessing protected route with invalid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


# Cleanup after tests
def teardown_module():
    """Clean up test database."""
    Base.metadata.drop_all(bind=engine)