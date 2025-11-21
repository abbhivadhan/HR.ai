"""
Data Encryption Service for sensitive information
"""
import base64
import os
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption service
        
        Args:
            encryption_key: Base64 encoded encryption key. If None, generates a new key.
        """
        if encryption_key:
            self.key = base64.urlsafe_b64decode(encryption_key.encode())
        else:
            self.key = Fernet.generate_key()
        
        self.fernet = Fernet(self.key)
    
    @classmethod
    def generate_key(cls) -> str:
        """Generate a new encryption key"""
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode()
    
    @classmethod
    def derive_key_from_password(cls, password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
        """
        Derive encryption key from password using PBKDF2
        
        Returns:
            Tuple of (key, salt) both base64 encoded
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        salt_b64 = base64.urlsafe_b64encode(salt).decode()
        
        return key.decode(), salt_b64
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data using Fernet symmetric encryption
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Base64 encoded encrypted data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = self.fernet.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data using Fernet symmetric encryption
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file
        
        Args:
            file_path: Path to file to encrypt
            output_path: Path for encrypted file (defaults to file_path + '.encrypted')
            
        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = file_path + '.encrypted'
        
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = self.fernet.encrypt(file_data)
        
        with open(output_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
        
        return output_path
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Path for decrypted file
            
        Returns:
            Path to decrypted file
        """
        if output_path is None:
            output_path = encrypted_file_path.replace('.encrypted', '')
        
        with open(encrypted_file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        
        decrypted_data = self.fernet.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)
        
        return output_path


class FieldEncryption:
    """Utility class for encrypting specific database fields"""
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
    
    def encrypt_pii(self, data: dict) -> dict:
        """
        Encrypt personally identifiable information in a dictionary
        
        Args:
            data: Dictionary containing PII fields
            
        Returns:
            Dictionary with encrypted PII fields
        """
        pii_fields = [
            'ssn', 'social_security_number', 'tax_id',
            'phone_number', 'address', 'date_of_birth',
            'passport_number', 'driver_license'
        ]
        
        encrypted_data = data.copy()
        
        for field in pii_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encryption_service.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_pii(self, data: dict) -> dict:
        """
        Decrypt personally identifiable information in a dictionary
        
        Args:
            data: Dictionary containing encrypted PII fields
            
        Returns:
            Dictionary with decrypted PII fields
        """
        pii_fields = [
            'ssn', 'social_security_number', 'tax_id',
            'phone_number', 'address', 'date_of_birth',
            'passport_number', 'driver_license'
        ]
        
        decrypted_data = data.copy()
        
        for field in pii_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.encryption_service.decrypt(decrypted_data[field])
                except ValueError:
                    # Field might not be encrypted, leave as is
                    pass
        
        return decrypted_data
    
    def encrypt_sensitive_fields(self, model_data: dict, sensitive_fields: list[str]) -> dict:
        """
        Encrypt specified sensitive fields in model data
        
        Args:
            model_data: Dictionary containing model data
            sensitive_fields: List of field names to encrypt
            
        Returns:
            Dictionary with encrypted sensitive fields
        """
        encrypted_data = model_data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encryption_service.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_sensitive_fields(self, model_data: dict, sensitive_fields: list[str]) -> dict:
        """
        Decrypt specified sensitive fields in model data
        
        Args:
            model_data: Dictionary containing encrypted model data
            sensitive_fields: List of field names to decrypt
            
        Returns:
            Dictionary with decrypted sensitive fields
        """
        decrypted_data = model_data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.encryption_service.decrypt(decrypted_data[field])
                except ValueError:
                    # Field might not be encrypted, leave as is
                    pass
        
        return decrypted_data


# Global encryption service instance
# In production, the key should be loaded from environment variables or key management service
_encryption_key = os.getenv('ENCRYPTION_KEY')
if not _encryption_key:
    # Generate a key for development (should be stored securely in production)
    _encryption_key = EncryptionService.generate_key()
    print(f"Generated encryption key: {_encryption_key}")
    print("Store this key securely and set ENCRYPTION_KEY environment variable")

encryption_service = EncryptionService(_encryption_key)
field_encryption = FieldEncryption(encryption_service)