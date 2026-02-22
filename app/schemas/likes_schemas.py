from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field


class LikeUserShortInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None


class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    user: LikeUserShortInfo


class LikeAction(BaseModel):
    post_id: int
    likes_count: int
    is_liked: bool
