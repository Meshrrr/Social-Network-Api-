from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class FollowUserInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None

class FollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime
    follower: FollowUserInfo
    following: FollowUserInfo

class FollowActionResponse(BaseModel):
    user_id: int
    is_following: bool
    followers_count: int
    following_count: int
    message: str