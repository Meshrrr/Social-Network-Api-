from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field


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
    username: Optional[str] = Field(None, description="Новый юзернейм пользователя")
    email: Optional[EmailStr] = Field(None, description="Новый email пользователя")
    full_name: Optional[str] = Field(None, description="Новое полное имя пользователя")
    bio: Optional[str] = Field(None, description="Новое 'о себе' пользователя")
