"""
Multi-Factor Authentication Service
Handles TOTP (Time-based One-Time Password) authentication
"""
import pyotp
import qrcode
from io import BytesIO
import base64
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from ..models.user import User
from ..database import get_db


class MFAService:
    """Service for handling Multi-Factor Authentication"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_secret_key(self) -> str:
        """Generate a new secret key for TOTP"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, user: User, secret_key: str) -> str:
        """Generate QR code for TOTP setup"""
        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=user.email,
            issuer_name="AI-HR Platform"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 string
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_totp_code(self, secret_key: str, code: str) -> bool:
        """Verify TOTP code"""
        try:
            totp = pyotp.TOTP(secret_key)
            return totp.verify(code, valid_window=1)  # Allow 1 window tolerance
        except Exception:
            return False
    
    def enable_mfa_for_user(self, user: User, secret_key: str) -> bool:
        """Enable MFA for a user"""
        try:
            user.mfa_secret = secret_key
            user.mfa_enabled = True
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def disable_mfa_for_user(self, user: User) -> bool:
        """Disable MFA for a user"""
        try:
            user.mfa_secret = None
            user.mfa_enabled = False
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def generate_backup_codes(self, user: User) -> list[str]:
        """Generate backup codes for MFA recovery"""
        import secrets
        import string
        
        backup_codes = []
        for _ in range(10):  # Generate 10 backup codes
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                          for _ in range(8))
            backup_codes.append(code)
        
        # Store hashed backup codes in database
        from ..auth.utils import get_password_hash
        hashed_codes = [get_password_hash(code) for code in backup_codes]
        user.mfa_backup_codes = hashed_codes
        self.db.commit()
        
        return backup_codes
    
    def verify_backup_code(self, user: User, code: str) -> bool:
        """Verify and consume a backup code"""
        if not user.mfa_backup_codes:
            return False
        
        from ..auth.utils import verify_password
        
        for i, hashed_code in enumerate(user.mfa_backup_codes):
            if verify_password(code, hashed_code):
                # Remove used backup code
                user.mfa_backup_codes.pop(i)
                self.db.commit()
                return True
        
        return False