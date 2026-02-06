# backend/utils/security.py
from cryptography.fernet import Fernet
import os

from backend.utils.logger import get_logger

logger = get_logger("Security")

# Load encryption key from environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    logger.error("ENCRYPTION_KEY not set in environment variables")
    raise ValueError("ENCRYPTION_KEY missing. Generate one using Fernet.generate_key()")

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_string(plaintext: str) -> str:
    try:
        encrypted = cipher_suite.encrypt(plaintext.encode()).decode()
        logger.debug("String encrypted successfully")
        return encrypted
    except Exception as e:
        logger.exception("Encryption failed")
        raise

def decrypt_string(ciphertext: str) -> str:
    try:
        decrypted = cipher_suite.decrypt(ciphertext.encode()).decode()
        logger.debug("String decrypted successfully")
        return decrypted
    except Exception as e:
        logger.exception("Decryption failed")
        raise
