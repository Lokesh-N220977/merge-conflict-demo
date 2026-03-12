import bcrypt


def hash_password(password: str) -> str:
    """Hash password using bcrypt directly (avoids passlib 72-byte bug)."""
    # bcrypt has a 72-byte limit. We truncate manually to avoid ValueError.
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt directly."""
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(
            password_bytes,
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False
