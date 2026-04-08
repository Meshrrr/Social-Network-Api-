import math
from typing import Optional


from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.schemas.followers_schemas import FollowUserInfo, FollowActionResponse, FollowerListResponse
from app.models import Follows, User, Notification, NotificationType
from api.v1.utils.auth.auth_utils import get_current_user
from app.api.v1.utils.notifications.notification_utils import create_notification, get_unread_count


router = APIRouter(prefix="/users", tags=["follows"])

@router.post('/{user_id}/follow', response_model=FollowActionResponse)
async def follow_toggle(user_id: int, current_user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):

    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя подписаться на самого себя")

    result = await db.execute(select(User).where(user_id == User.id))

    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Такого пользователя нет")

    check_follow = await db.execute(select(Follows).where(Follows.follower_id == current_user.id,
                                                          Follows.following_id == user_id))

    exist_follow = check_follow.scalar_one_or_none()

    if exist_follow:
        await db.delete(exist_follow)
        is_following = False
        message = "Вы отписались от пользователя"

    else:
        new_follow = Follows(
            follower_id=current_user.id,
            following_id=user_id,
        )
        db.add(new_follow)
        is_following = True
        message = "Вы подписались на пользователя"

    await db.commit()

    followers_count = await db.scalar(
        select(func.count(Follows.id)).where(Follows.following_id == user_id)
    )

    following_count = await db.scalar(
        select(func.count(Follows.id)).where(Follows.follower_id == user_id)
    )

    if not exist_follow and user_id != current_user.id:
        await create_notification(
            db=db,
            type=NotificationType.FOLLOW,
            user_id=user_id,
            actor_id=current_user.id
        )s

    return FollowActionResponse(is_following=is_following,
                                user_id=user_id,
                                followers_count=followers_count,
                                following_count=following_count,
                                message=message)



@router.get('/{user_id}/followers', response_model=FollowerListResponse)
async def get_followers(user_id: int,
                        page: int = Query(1, ge=1),
                        page_size: int = Query(20, ge=1, le=100),
                        db: AsyncSession = Depends(get_db),
                        current_user: Optional[User] = Depends(get_current_user),
                        ):

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    total_subs = await db.scalar(select(func.count(Follows.id)).where(Follows.following_id == user_id))

    offset = (page - 1) * page_size

    result = await db.execute(select(Follows).where(Follows.following_id == user_id).options(selectinload(Follows.follower)).offset(offset).limit(page_size))

    follows = result.scalars().all()


    followers = []

    for follow in follows:
        user_info = FollowUserInfo.model_validate(follow.follower)
        followers.append(user_info)


    total_pages = math.ceil(total_subs / page_size) if total_subs > 0 else 1


    return {
        "followers": followers,
        "total": total_pages,
        "page":page,
        "page_size":page_size,
        "total_pages": total_pages
    }


@router.get("/{user_id}", response_model=FollowerListResponse)
async def get_following(user_id: int,
                        page: int = Query(1, ge=1),
                        page_size = Query(20, ge=1, le=100),
                        current_user: Optional[User] = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    total_follows = await db.scalar(select(func.count(Follows.id)).where(Follows.follower_id == user_id))

    offset = (page - 1) * page_size

    result = await db.execute(select(Follows).where(Follows.follower_id == user_id).options(selectinload(Follows.following)).offset(offset).limit(page_size))

    follows = result.scalars().all()

    following = []
    for follow in follows:
        user_info = FollowUserInfo.model_validate(follow.following)
        following.append(user_info)

    total_pages = math.ceil(total_follows / page_size) if total_follows > 0 else 1

    return {
        "items": following,
        "total": total_follows,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.post("{user_id}/follow_status")
async def check_follow_status(user_id: int,
                              current_user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):

    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Это вы")

    result = await db.execute(select(Follows).where(Follows.following_id == user_id,
                                                    Follows.follower_id == current_user.id))

    follow = result.scalar_one_or_none()

    return {
        "is_following": follow is not None,
        "follower_id": current_user.id,
        "following_id": user_id
    }