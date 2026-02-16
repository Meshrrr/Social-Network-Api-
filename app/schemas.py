from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field

#ALL FOR USER

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

#PASSWORD

class PasswordUpdate(BaseModel):
    current_password: str = Field(description="Ваш текущий пароль")
    new_password: str = Field(description="Ваш новый пароль", min_length=5, max_length=20)
    confirm_password: str = Field(description="Подтвердите ваш новый пароль", min_length=5, max_length=20)

#POSTS

class Post(BaseModel):
    body: str = Field(description="Тело поста", min_length=5, max_length=280)
    image_url: Optional[str] = Field(description="url прикрепленного изображения")

class PostUpdate(BaseModel):
    body: Optional[str] = Field(description="Тело поста", min_length=5, max_length=280)
    image_url: Optional[str] = Field(description="url прикрепленного изображения")


class UserShortInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class PostResponse(Post):
    id: int = Field(..., description="ID поста")
    user_id: int = Field(..., description="ID автора")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    user: Optional[UserShortInfo] = Field(None, description="Информация об авторе")
    likes_count: int = Field(0, description="Количество лайков")
    comments_count: int = Field(0, description="Количество комментариев")
    is_liked: bool = Field(False, description="Лайкнул ли текущий пользователь")
    is_owner: bool = Field(False, description="Является ли текущий пользователь автором")