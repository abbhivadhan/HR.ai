from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from ..models.user import User, UserType
from ..schemas.auth import UserRegistration, UserLogin
from ..auth.utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_verification_token,
    generate_reset_token
)
from .mfa_service import MFAService
from .audit_service import AuditService
from .rate_limit_service import RateLimitService
from .security_monitoring_service import SecurityMonitoringService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.mfa_service = MFAService(db)
        self.audit_service = AuditService(db)
        self.rate_limit_service = RateLimitService(self.audit_service)
        self.security_monitoring = SecurityMonitoringService(db)

    def register_user(self, user_data: UserRegistration) -> User:
        """Register a new user."""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        verification_token = generate_verification_token()
        
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            user_type=user_data.user_type,
            verification_token=verification_token
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # TODO: Send verification email (will be implemented in notification service)
        
        return new_user

    def authenticate_user(self, login_data: UserLogin, request: Optional[Request] = None) -> Optional[User]:
        """Authenticate user credentials with enhanced security."""
        ip_address = self._get_client_ip(request) if request else "unknown"
        user_agent = request.headers.get("user-agent", "") if request else ""
        
        # Check rate limiting
        if not self.rate_limit_service.check_login_rate_limit(ip_address, login_data.email):
            self.audit_service.log_login_attempt(
                email=login_data.email,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )
        
        user = self.db.query(User).filter(User.email == login_data.email).first()
        
        # Check if account is locked
        if user and user.locked_until and user.locked_until > datetime.utcnow():
            self.audit_service.log_login_attempt(
                email=login_data.email,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                user=user
            )
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to suspicious activity"
            )
        
        if not user:
            # Log failed attempt
            self.audit_service.log_login_attempt(
                email=login_data.email,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent
            )
            # Increment failed login attempts
            self.rate_limit_service.increment_failed_login(ip_address, login_data.email)
            return None
            
        if not verify_password(login_data.password, user.password_hash):
            # Log failed attempt
            self.audit_service.log_login_attempt(
                email=login_data.email,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                user=user
            )
            
            # Handle failed login attempts
            failed_attempts = int(user.failed_login_attempts or "0") + 1
            user.failed_login_attempts = str(failed_attempts)
            
            # Lock account after 5 failed attempts
            if failed_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(hours=1)
                self.audit_service.log_security_event(
                    event_type="ACCOUNT_LOCKED",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    user=user,
                    details={"reason": "too_many_failed_attempts", "attempts": failed_attempts}
                )
            
            self.db.commit()
            return None
            
        if not user.is_active:
            self.audit_service.log_login_attempt(
                email=login_data.email,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                user=user
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is deactivated"
            )
        
        # Reset failed login attempts on successful authentication
        user.failed_login_attempts = "0"
        user.locked_until = None
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Check for account takeover attempts
        if request:
            self.security_monitoring.detect_account_takeover(user, request)
        
        return user

    def create_tokens(self, user: User) -> dict:
        """Create access and refresh tokens for user."""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "user_type": user.user_type.value
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900  # 15 minutes in seconds
        }

    def verify_email(self, token: str) -> bool:
        """Verify user email with token."""
        user = self.db.query(User).filter(User.verification_token == token).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
            
        user.is_verified = True
        user.verification_token = None
        self.db.commit()
        
        return True

    def request_password_reset(self, email: str) -> bool:
        """Request password reset for user."""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists for security
            return True
            
        reset_token = generate_reset_token()
        reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        
        user.reset_token = reset_token
        user.reset_token_expires = reset_expires
        self.db.commit()
        
        # TODO: Send password reset email (will be implemented in notification service)
        
        return True

    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password with token."""
        user = self.db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
            
        user.password_hash = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        self.db.commit()
        
        return True

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def setup_mfa(self, user: User) -> dict:
        """Setup MFA for user."""
        secret_key = self.mfa_service.generate_secret_key()
        qr_code = self.mfa_service.generate_qr_code(user, secret_key)
        
        return {
            "secret_key": secret_key,
            "qr_code": qr_code,
            "backup_codes": []  # Will be generated after verification
        }
    
    def verify_mfa_setup(self, user: User, secret_key: str, totp_code: str) -> dict:
        """Verify MFA setup and enable it."""
        if not self.mfa_service.verify_totp_code(secret_key, totp_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code"
            )
        
        # Enable MFA for user
        self.mfa_service.enable_mfa_for_user(user, secret_key)
        
        # Generate backup codes
        backup_codes = self.mfa_service.generate_backup_codes(user)
        
        self.audit_service.log_action(
            action="MFA_ENABLED",
            user=user,
            resource="authentication",
            details={"method": "TOTP"}
        )
        
        return {
            "enabled": True,
            "backup_codes": backup_codes
        }
    
    def verify_mfa_login(self, user: User, totp_code: str, backup_code: Optional[str] = None) -> bool:
        """Verify MFA during login."""
        if not user.mfa_enabled:
            return True
        
        # Try TOTP code first
        if totp_code and self.mfa_service.verify_totp_code(user.mfa_secret, totp_code):
            return True
        
        # Try backup code if provided
        if backup_code and self.mfa_service.verify_backup_code(user, backup_code):
            self.audit_service.log_action(
                action="MFA_BACKUP_CODE_USED",
                user=user,
                resource="authentication",
                details={"backup_codes_remaining": len(user.mfa_backup_codes or [])}
            )
            return True
        
        # Log failed MFA attempt
        self.audit_service.log_security_event(
            event_type="MFA_BYPASS_ATTEMPT",
            user=user,
            details={"totp_provided": bool(totp_code), "backup_code_provided": bool(backup_code)}
        )
        
        return False
    
    def disable_mfa(self, user: User, current_password: str) -> bool:
        """Disable MFA for user (requires password confirmation)."""
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password"
            )
        
        success = self.mfa_service.disable_mfa_for_user(user)
        
        if success:
            self.audit_service.log_action(
                action="MFA_DISABLED",
                user=user,
                resource="authentication"
            )
        
        return success
    
    def generate_new_backup_codes(self, user: User) -> list[str]:
        """Generate new backup codes for user."""
        if not user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not enabled"
            )
        
        backup_codes = self.mfa_service.generate_backup_codes(user)
        
        self.audit_service.log_action(
            action="MFA_BACKUP_CODES_REGENERATED",
            user=user,
            resource="authentication",
            details={"codes_count": len(backup_codes)}
        )
        
        return backup_codes
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"