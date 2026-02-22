from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    body: str = Field(description="Тело поста", min_length=5, max_length=280)
    image_url: Optional[str] = Field(None, description="url прикрепленного изображения")

class PostUpdate(BaseModel):
    body: Optional[str] = Field(description="Тело поста", min_length=5, max_length=280)
    image_url: Optional[str] = Field(None, description="url прикрепленного изображения")


class UserShortInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class PostResponse(PostBase):
    id: int = Field(..., description="ID поста")
    user_id: int = Field(..., description="ID автора")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    user: Optional[UserShortInfo] = Field(None, description="Информация об авторе")
    likes_count: int = Field(0, description="Количество лайков")
    comments_count: int = Field(0, description="Количество комментариев")
    is_liked: bool = Field(False, description="Лайкнул ли текущий пользователь")
    is_owner: bool = Field(False, description="Является ли текущий пользователь автором")