from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"])


def get_hashed_password(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(password, hashed_password)
