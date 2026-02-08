from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class createUser(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    #Должны быть указаны типы которые мы передали:
    model_config = ConfigDict(strict=True)
    username: str
    bio: Optional[str] = None
    full_name: Optional[str] = None
    email: EmailStr | None = None
    is_active: bool = True
    created_at: Optional[datetime] = datetime.now()

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None

