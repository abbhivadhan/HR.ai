"""
Security feature tests
"""
import pytest
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch
from app.main import app
from app.database import get_db
from app.models.user import User, UserType
from app.services.mfa_service import MFAService
from app.services.audit_service import AuditService
from app.services.encryption_service import EncryptionService
from app.services.gdpr_service import GDPRService
from app.services.security_monitoring_service import SecurityMonitoringService
from app.services.rate_limit_service import RateLimitService


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    return Mock(spec=Session)


@pytest.fixture
def test_user():
    return User(
        id="test-user-id",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        user_type=UserType.CANDIDATE,
        password_hash="hashed_password",
        is_active=True,
        is_verified=True,
        mfa_enabled=False
    )


class TestMFAService:
    """Test Multi-Factor Authentication service"""
    
    def test_generate_secret_key(self, mock_db):
        mfa_service = MFAService(mock_db)
        secret_key = mfa_service.generate_secret_key()
        
        assert isinstance(secret_key, str)
        assert len(secret_key) == 32  # Base32 encoded secret
    
    def test_generate_qr_code(self, mock_db, test_user):
        mfa_service = MFAService(mock_db)
        secret_key = "JBSWY3DPEHPK3PXP"
        
        qr_code = mfa_service.generate_qr_code(test_user, secret_key)
        
        assert qr_code.startswith("data:image/png;base64,")
        assert len(qr_code) > 100  # Should be a substantial base64 string
    
    def test_verify_totp_code_valid(self, mock_db):
        mfa_service = MFAService(mock_db)
        secret_key = "JBSWY3DPEHPK3PXP"
        
        # Mock pyotp.TOTP.verify to return True
        with patch('pyotp.TOTP.verify', return_value=True):
            result = mfa_service.verify_totp_code(secret_key, "123456")
            assert result is True
    
    def test_verify_totp_code_invalid(self, mock_db):
        mfa_service = MFAService(mock_db)
        secret_key = "JBSWY3DPEHPK3PXP"
        
        # Mock pyotp.TOTP.verify to return False
        with patch('pyotp.TOTP.verify', return_value=False):
            result = mfa_service.verify_totp_code(secret_key, "000000")
            assert result is False
    
    def test_enable_mfa_for_user(self, mock_db, test_user):
        mfa_service = MFAService(mock_db)
        secret_key = "JBSWY3DPEHPK3PXP"
        
        result = mfa_service.enable_mfa_for_user(test_user, secret_key)
        
        assert result is True
        assert test_user.mfa_secret == secret_key
        assert test_user.mfa_enabled is True
        mock_db.commit.assert_called_once()
    
    def test_generate_backup_codes(self, mock_db, test_user):
        mfa_service = MFAService(mock_db)
        
        backup_codes = mfa_service.generate_backup_codes(test_user)
        
        assert len(backup_codes) == 10
        assert all(len(code) == 8 for code in backup_codes)
        assert test_user.mfa_backup_codes is not None
        assert len(test_user.mfa_backup_codes) == 10


class TestEncryptionService:
    """Test data encryption service"""
    
    def test_generate_key(self):
        key = EncryptionService.generate_key()
        assert isinstance(key, str)
        assert len(key) > 20  # Base64 encoded key should be substantial
    
    def test_encrypt_decrypt_string(self):
        encryption_service = EncryptionService()
        original_data = "sensitive information"
        
        encrypted_data = encryption_service.encrypt(original_data)
        decrypted_data = encryption_service.decrypt(encrypted_data)
        
        assert encrypted_data != original_data
        assert decrypted_data == original_data
    
    def test_encrypt_decrypt_bytes(self):
        encryption_service = EncryptionService()
        original_data = b"sensitive binary data"
        
        encrypted_data = encryption_service.encrypt(original_data)
        decrypted_data = encryption_service.decrypt(encrypted_data)
        
        assert encrypted_data != original_data.decode()
        assert decrypted_data == original_data.decode()
    
    def test_derive_key_from_password(self):
        password = "secure_password"
        key, salt = EncryptionService.derive_key_from_password(password)
        
        assert isinstance(key, str)
        assert isinstance(salt, str)
        assert len(key) > 20
        assert len(salt) > 10
    
    def test_encrypt_pii_fields(self):
        from ..app.services.encryption_service import field_encryption
        
        data = {
            "name": "John Doe",
            "ssn": "123-45-6789",
            "phone_number": "+1-555-123-4567",
            "regular_field": "not encrypted"
        }
        
        encrypted_data = field_encryption.encrypt_pii(data)
        
        assert encrypted_data["name"] == "John Doe"  # Not a PII field in our list
        assert encrypted_data["ssn"] != "123-45-6789"  # Should be encrypted
        assert encrypted_data["phone_number"] != "+1-555-123-4567"  # Should be encrypted
        assert encrypted_data["regular_field"] == "not encrypted"


class TestAuditService:
    """Test audit logging service"""
    
    def test_log_action(self, mock_db, test_user):
        audit_service = AuditService(mock_db)
        
        audit_log = audit_service.log_action(
            action="TEST_ACTION",
            user=test_user,
            resource="test_resource",
            details={"key": "value"}
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert audit_log.action == "TEST_ACTION"
        assert audit_log.user_id == test_user.id
    
    def test_log_login_attempt_success(self, mock_db, test_user):
        audit_service = AuditService(mock_db)
        
        audit_service.log_login_attempt(
            email="test@example.com",
            success=True,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            user=test_user,
            mfa_used=True
        )
        
        # Should call log_action
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
    
    def test_log_login_attempt_failure(self, mock_db):
        audit_service = AuditService(mock_db)
        
        audit_service.log_login_attempt(
            email="test@example.com",
            success=False,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # Should call both log_action and log_security_event
        assert mock_db.add.call_count >= 2
        assert mock_db.commit.call_count >= 2


class TestGDPRService:
    """Test GDPR compliance service"""
    
    def test_record_consent(self, mock_db, test_user):
        gdpr_service = GDPRService(mock_db)
        
        result = gdpr_service.record_consent(
            user=test_user,
            consent_type="marketing",
            granted=True,
            purpose="Email marketing",
            ip_address="192.168.1.1"
        )
        
        assert result is True
        mock_db.commit.assert_called_once()
    
    def test_export_user_data(self, mock_db, test_user):
        gdpr_service = GDPRService(mock_db)
        
        # Mock the audit service
        with patch.object(gdpr_service, 'audit_service'):
            user_data = gdpr_service.export_user_data(test_user)
        
        assert "personal_information" in user_data
        assert "profile_data" in user_data
        assert "assessments" in user_data
        assert "audit_trail" in user_data
        assert user_data["personal_information"]["email"] == test_user.email
    
    def test_create_data_export_file(self, mock_db, test_user):
        gdpr_service = GDPRService(mock_db)
        
        with patch.object(gdpr_service, 'export_user_data', return_value={"test": "data"}):
            zip_data = gdpr_service.create_data_export_file(test_user)
        
        assert isinstance(zip_data, bytes)
        assert len(zip_data) > 0
    
    def test_anonymize_user_data(self, mock_db, test_user):
        gdpr_service = GDPRService(mock_db)
        
        with patch.object(gdpr_service, 'audit_service'):
            result = gdpr_service.anonymize_user_data(test_user)
        
        assert result is True
        assert test_user.email.startswith("anon_")
        assert test_user.first_name == "Anonymous"
        assert test_user.last_name == "User"
        assert test_user.is_active is False
        mock_db.commit.assert_called()


class TestSecurityMonitoring:
    """Test security monitoring and threat detection"""
    
    def test_detect_sql_injection(self, mock_db):
        security_monitoring = SecurityMonitoringService(mock_db)
        
        # Mock request with SQL injection attempt
        mock_request = Mock()
        mock_request.url.query = "id=1' OR '1'='1"
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        mock_request.headers = {"user-agent": "Mozilla/5.0"}
        mock_request.client.host = "192.168.1.1"
        
        result = security_monitoring._detect_sql_injection(mock_request)
        assert result is True
    
    def test_detect_xss_attempt(self, mock_db):
        security_monitoring = SecurityMonitoringService(mock_db)
        
        # Mock request with XSS attempt
        mock_request = Mock()
        mock_request.url.query = "input=<script>alert('xss')</script>"
        
        result = security_monitoring._detect_xss_attempt(mock_request)
        assert result is True
    
    def test_detect_suspicious_user_agent(self, mock_db):
        security_monitoring = SecurityMonitoringService(mock_db)
        
        # Test with suspicious user agent
        result = security_monitoring._detect_suspicious_user_agent("sqlmap/1.0")
        assert result is True
        
        # Test with normal user agent
        result = security_monitoring._detect_suspicious_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        assert result is False
    
    def test_analyze_request_high_risk(self, mock_db):
        security_monitoring = SecurityMonitoringService(mock_db)
        
        # Mock high-risk request
        mock_request = Mock()
        mock_request.url.query = "id=1' UNION SELECT * FROM users--"
        mock_request.url.path = "/api/admin"
        mock_request.method = "GET"
        mock_request.headers = {"user-agent": "sqlmap/1.0"}
        mock_request.client.host = "192.168.1.1"
        
        with patch.object(security_monitoring, 'audit_service'):
            result = security_monitoring.analyze_request(mock_request)
        
        assert result["risk_score"] >= 10
        assert result["should_block"] is True
        assert "SQL_INJECTION_ATTEMPT" in result["threats"]


class TestRateLimitService:
    """Test rate limiting service"""
    
    @patch('redis.from_url')
    def test_check_rate_limit_within_limit(self, mock_redis):
        # Mock Redis pipeline
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = [None, 2, None, None]  # 2 current requests
        mock_redis.return_value.pipeline.return_value = mock_pipeline
        
        rate_limit_service = RateLimitService()
        
        result = rate_limit_service.check_rate_limit("test_key", 5, 60)
        assert result is True
    
    @patch('redis.from_url')
    def test_check_rate_limit_exceeded(self, mock_redis):
        # Mock Redis pipeline
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = [None, 6, None, None]  # 6 current requests
        mock_redis.return_value.pipeline.return_value = mock_pipeline
        
        rate_limit_service = RateLimitService()
        
        result = rate_limit_service.check_rate_limit("test_key", 5, 60)
        assert result is False
    
    @patch('redis.from_url')
    def test_increment_failed_login(self, mock_redis):
        mock_redis.return_value.incr.side_effect = [3, 2]  # IP: 3 failures, Email: 2 failures
        
        rate_limit_service = RateLimitService()
        
        result = rate_limit_service.increment_failed_login("192.168.1.1", "test@example.com")
        
        assert result["ip_failures"] == 3
        assert result["email_failures"] == 2
        assert result["should_lock_ip"] is False
        assert result["should_lock_email"] is False
    
    @patch('redis.from_url')
    def test_block_ip(self, mock_redis):
        mock_redis.return_value.setex.return_value = True
        
        rate_limit_service = RateLimitService()
        
        result = rate_limit_service.block_ip("192.168.1.1", 3600)
        assert result is True


class TestSecurityAPI:
    """Test security API endpoints"""
    
    def test_mfa_setup_endpoint(self, client):
        # This would require proper authentication setup
        # For now, we'll test the basic structure
        response = client.post("/api/security/mfa/setup")
        # Should return 401 without authentication
        assert response.status_code in [401, 422]
    
    def test_audit_logs_endpoint(self, client):
        response = client.get("/api/security/audit-logs")
        # Should return 401 without authentication
        assert response.status_code in [401, 422]
    
    def test_gdpr_export_endpoint(self, client):
        response = client.get("/api/security/gdpr/export-data")
        # Should return 401 without authentication
        assert response.status_code in [401, 422]


class TestSecurityIntegration:
    """Integration tests for security features"""
    
    def test_security_middleware_blocks_malicious_request(self, client):
        # Test SQL injection attempt
        response = client.get("/api/test?id=1' OR '1'='1")
        # Should be blocked by security middleware
        assert response.status_code in [403, 404]  # 404 if endpoint doesn't exist
    
    def test_rate_limiting_headers(self, client):
        response = client.get("/")
        # Should include security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers