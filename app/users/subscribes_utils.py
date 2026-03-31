from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.followers_schemas import FollowUserInfo, FollowResponse, FollowActionResponse
from app.models import Follows, User
from app.auth.auth_utils import get_current_user

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

    return FollowActionResponse(is_following=is_following,
                                user_id=user_id,
                                followers_count=followers_count,
                                following_count=following_count,
                                message=message)



