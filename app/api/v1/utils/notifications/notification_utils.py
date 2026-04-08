from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Notification, NotificationType
from app.models import User


async def create_notification(
        db: AsyncSession,
        type: NotificationType,
        user_id: int,
        actor_id: int,
        object_id: int = None) -> Notification:

    if user_id == actor_id:
        return None

    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        notify_type=type,
        object_id=object_id
    )

    db.add(notification)

    await db.commit()
    await db.refresh(notification)

    return notification

async def get_unread_count(
        db: AsyncSession,
        user_id: int) -> int:

    result = await db.execute(select(func.count(Notification.id)).where(Notification.user_id == user_id,
                                                                        Notification.is_read == False))

    unread_notification = result.scalar()

    return unread_notification or 0