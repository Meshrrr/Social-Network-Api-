from datetime import datetime, timedelta
from pathlib import Path
import bcrypt
import jwt
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Form, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User

from app.schemas import (
createUser,
UserLogin,
UserUpdate,
UserResponse,
TokenResponse,
)

BASE_DIR = Path(__file__).parent.parent

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    TOKEN_EXPIRES_MINUTES: int = 30

auth_jwt = AuthJWT()

http_bearer = HTTPBearer()

def encode_jwt(
        payload: dict,
        private_key: str = auth_jwt.private_key_path.read_text(),
        algorithm: str = auth_jwt.algorithm,
        exp_minutes: int = auth_jwt.TOKEN_EXPIRES_MINUTES,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=exp_minutes)
    to_encode.update(exp=expire,
                     iat=now,)
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded

def decode_jwt(
        token: str,
        public_key: str = auth_jwt.public_key_path.read_text(),
        algorithm: str = auth_jwt.algorithm,
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    hashed_bytes =  bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode("utf-8")

def valid_password(
        password: str,
        hashed_password: str,
) -> bool:
    return bcrypt.checkpw(password=password.encode(),
                          hashed_password=hashed_password.encode("utf-8"))


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/", response_model=TokenResponse)
async def register(
        user_data:createUser,
        db: AsyncSession = Depends(get_db),
):
    hashed_pwd = hash_password(user_data.password)

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    token_payload = {
        "sub": str(user.id), #sub == user id
        "email": user.email,
        "username": user.username,
    }

    access_token = encode_jwt(token_payload)

    return TokenResponse(access_token=access_token,
                         token_type="bearer",)

@router.post("/login/", response_model=TokenResponse)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(User).where(User.username == user_login.username)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя Пользователя или пароль!")

    if not valid_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверное имя Пользователя или пароль!')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Аккаунт деактивирован')

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "username": user.username,
    }

    access_token = encode_jwt(token_payload)

    return TokenResponse(access_token=access_token,
                         token_type="bearer")

@router.get("/me/", response_model=UserResponse)
async def user_check_self(access_token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_jwt(access_token)

    user_id = int(payload["sub"])

    result = await db.execute(Select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Профиль недоступен")



    return UserResponse(username=user.username,
                        email=user.email,
                        bio=user.bio,
                        full_name=user.full_name,)
