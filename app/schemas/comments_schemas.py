from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from app.schemas.post_schemas import UserShortInfo


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int]

class CommentsBase(CommentCreate):
    id: int


class CommentsResponse(CommentsBase):
    user: UserShortInfo
    post_id: int
    created_at: datetime
    parent_id: Optional[int] = None

    is_owner: bool


class CommentResponseWithReplies(CommentsResponse):
    replies: list[CommentsResponse]

