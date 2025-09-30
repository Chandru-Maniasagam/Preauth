"""
Encryption utilities for RCM SaaS Application
"""

import hashlib
import secrets
from cryptography.fernet import Fernet
from typing import Union
import base64


def generate_key() -> bytes:
    """Generate a new encryption key"""
    return Fernet.generate_key()


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash a password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Combine password and salt
    salted_password = password + salt
    
    # Hash using SHA-256
    hashed = hashlib.sha256(salted_password.encode()).hexdigest()
    
    return hashed, salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify a password against its hash"""
    test_hash, _ = hash_password(password, salt)
    return test_hash == hashed_password


def encrypt_data(data: str, key: bytes) -> str:
    """Encrypt data using Fernet encryption"""
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()


def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt data using Fernet encryption"""
    f = Fernet(key)
    decoded_data = base64.b64decode(encrypted_data.encode())
    decrypted_data = f.decrypt(decoded_data)
    return decrypted_data.decode()


def generate_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def hash_data(data: str) -> str:
    """Generate a hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()
