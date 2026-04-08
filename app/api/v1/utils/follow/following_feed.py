from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException,status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Post, User, Follows, Like
from app.schemas.post_schemas import PostResponse
from app.api.v1.utils.auth.auth_utils import get_current_user

router = APIRouter(prefix="/feed", tags=["feed"])

@router.get('/', response_model=List[PostResponse])
async def get_feed(db: AsyncSession = Depends(get_db)):

    result_all = await db.execute(select(Post).order_by(Post.created_at.desc()))

    posts = result_all.scalars().all()

    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Посты не найдены")


    for post in posts:
        res = await db.execute(select(User).where(User.id == post.user_id))
        post.user = res.scalar_one_or_none()

    return posts

@router.get("/following", response_model=List[PostResponse])
async def get_follow_feed(limit: int = Query(20, ge=1, le=100),
                          offset: int = Query(0, ge=0),
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Follows.following_id).where(Follows.follower_id == current_user.id))

    following_ids = result.scalars().all()

    if not following_ids:
        return []

    result_posts = await db.execute(select(Post).where(Post.user_id.in_(following_ids))
                                    .options(selectinload(Post.user)).order_by(desc(Post.created_at))
                                    .offset(offset).limit(limit))

    result_posts = result_posts.scalars().all()

    for post in result_posts:
        result = await db.execute(select(Like).where(
            Like.post_id == post.id,
            Like.user_id == current_user.id
            )
        )
        post.is_liked = result.scalar_one_or_none() is not None
        post.is_owner = False

        counter_likes = await db.execute(select(func.count(Like.id)).where(Like.post_id == post.id))

        post.likes_count = counter_likes.scalar()

    return result_posts
