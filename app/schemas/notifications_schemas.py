from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class NotificationType(BaseModel):
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    REPLY = "reply"

class NotificationBase(BaseModel):
    type = NotificationType
    actor_id: int
    object_id: int

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    unread_count: int
    total: int
    page: int
    page_size: int
    total_page: int

class MarkReadRequest(BaseModel):
    notification_ids: Optional[list[int]] = None  # None = все прочитать