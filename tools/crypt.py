import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

import bcrypt

from envparse import env

env.read_envfile()

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=env.str('SALT').encode(),
    iterations=100000,
    backend=default_backend()
)


key = base64.urlsafe_b64encode(kdf.derive(env.str('PASSWORD').encode()))
f = Fernet(key)


def encrypt(data: str) -> str:
    """Шифрует данные алгоритмом"""

    encrypted_data = f.encrypt(data.encode()).decode()
    return encrypted_data


def decrypt(encr_data: str) -> str:
    """Расшифровывает данные"""

    decrypted_data = f.decrypt(encr_data).decode()
    return decrypted_data


def encrypt_password(password: str) -> str:
    """Шифрует пароль алгоритмом bcrypt"""

    encrypted_password = bcrypt.hashpw(password.encode(), os.environ['SALT'].encode())
    return encrypted_password.decode()