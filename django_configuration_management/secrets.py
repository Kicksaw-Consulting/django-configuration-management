import os

from cryptography.fernet import Fernet


def encrypt_value(value: str, encoding="utf-8"):
    fernet = Fernet(os.getenv("ENC_KEY"))

    encrypted = fernet.encrypt(bytes(value, encoding))

    return encrypted.decode(encoding)


def decrypt_value(value: str, encoding="utf-8"):
    fernet = Fernet(os.getenv("ENC_KEY"))

    decrypted = fernet.decrypt(bytes(value, encoding))

    return decrypted.decode(encoding)


def generate_fernet_key():
    key = Fernet.generate_key()

    return key.decode("utf-8")
