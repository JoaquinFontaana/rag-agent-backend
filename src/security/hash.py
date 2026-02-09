from passlib.context import CryptContext

# Configure password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bcrypt has a maximum password length of 72 bytes
MAX_PASSWORD_LENGTH = 72


def hash_password(password: str) -> str:
    """Hash a password using bcrypt. Truncates to 72 bytes to comply with bcrypt limits."""
    # Truncate password to 72 bytes to avoid bcrypt ValueError
    truncated_password = password.encode('utf-8')[:MAX_PASSWORD_LENGTH].decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash. Truncates to 72 bytes to comply with bcrypt limits."""
    # Truncate password to 72 bytes to avoid bcrypt ValueError
    truncated_password = plain_password.encode('utf-8')[:MAX_PASSWORD_LENGTH].decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)
