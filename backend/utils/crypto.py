import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
fernet = Fernet(os.getenv("FERNET_KEY"))

def encrypt(text: str) -> str:
    try:
        return fernet.encrypt(text.encode()).decode()
    except Exception as e:
        print("DECRYPTION ERROR:", e)
        raise


def decrypt(token: str) -> str:
    try:
        return fernet.decrypt(token.encode()).decode()
    except Exception as e:
        print("DECRYPTION ERROR:", e)
        raise