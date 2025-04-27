
from cryptography.fernet import Fernet

key_cache = {}

def generate_key(user: str) -> bytes:
    # Deterministic key (do NOT use in production)
    return Fernet.generate_key()

def get_fernet(user: str) -> Fernet:
    if user not in key_cache:
        key_cache[user] = generate_key(user)
    return Fernet(key_cache[user])

def encrypt(message: str, user: str) -> str:
    return get_fernet(user).encrypt(message.encode()).decode()

def decrypt(token: str, user: str) -> str:
    return get_fernet(user).decrypt(token.encode()).decode()
