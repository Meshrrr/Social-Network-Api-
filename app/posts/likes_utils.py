from fastapi import APIRouter, HTTPException, Depends, status
from mako.testing.helpers import result_raw_lines
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.likes_schemas import LikeUserShortInfo, LikeAction, LikeResponse
from app.models import User, Post, Like
from app.database import get_db
from app.auth.auth_utils import get_current_user

router = APIRouter(prefix="/posts", tags=["likes"])

router.post("/{post_id}/like", response_model=LikeAction)
async def toggle_like(post_id: int,
                      current_user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))

    current_post = result.scalar_one_or_none()
    if not current_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Такого поста не существует")


    result_is_liked = await db.execute(select(Like).where(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ))

    current_like = result_is_liked.scalar_one_or_none()

    if current_like:
        await db.delete(current_like)
        await db.commit()
        is_liked = False
    else:
        new_like = Like(
            user_id=current_user.id,
            post_id=post_id,
        )
        is_liked = True

        db.add(new_like)
        await db.commit()


    result_all_likes = await db.execute(select(func.count(Like.id)).where(Like.post_id == post_id))
    likes_count = result_all_likes.scalar()

    return LikeAction(
        post_id=post_id,
        likes_count=likes_count,
        is_liked=is_liked,
    )

