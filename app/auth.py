import hashlib


def hash_password_bcrypt_like(plain: str) -> str:
    # Minimal placeholder: in production use passlib[bcrypt].
    # Using sha256 here to avoid extra deps per user request.
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password_bcrypt_like(plain) == hashed


