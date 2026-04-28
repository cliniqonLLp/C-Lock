from cryptography.fernet import Fernet
from app.config import settings

fernet = Fernet(settings.FERNET_KEY.encode())


def encrypt_text(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt_text(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()