from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from app.schemas.post_schemas import UserShortInfo

class CommentsBase(BaseModel):
    id: int
    content:str

class CommentsResponse(BaseModel):
    user: UserShortInfo
    post_id: int
    created_at: datetime
    parent_id: Optional[int] = None

    is_owner: bool

