import hashlib
import os
from pathlib import Path
import bcrypt

import jwt
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"

auth_jwt = AuthJWT()

def encode_jwt(
        payload: dict,
        private_key: str = auth_jwt.private_key_path.read_text(),
        algorithm: str = auth_jwt.algorithm,
):
    encoded = jwt.encode(payload, key, algorithm=algorithm)
    return encoded

def decode_jwt(
        token: str,
        public_key: str = auth_jwt.public_key_path.read_text(),
        algorithm: str = auth_jwt.algorithm,
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)

def valid_password(
        password: str,
        hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(password=password.encode(),
                          hashed_password=hashed_password)
