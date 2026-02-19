from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, Select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Post, User
from app.schemas import PostBase, PostUpdate, PostResponse, UserShortInfo
from app.auth.auth_utils import get_current_user


router = APIRouter(prefix="/posts", tags=["posts"])

@router.post('/', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, current_user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db),):

    post = Post(
        body=post.body,
        image_url=post.image_url,
        user_id=current_user.id
    )

    db.add(post)
    await db.commit()
    await db.refresh(post)

    return post

#реализовать ленту потом
@router.get('/feed', response_model=List[PostResponse])
async def get_feed(current_user: Optional[User] = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):

    result_all = await db.execute(select(Post).order_by(Post.created_at.desc()))

    posts = result_all.scalars().all()

    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Посты не найдены")


    for post in posts:
        res = await db.execute(select(User).where(User.id == post.user_id))
        post.user = res.scalar_one_or_none()

    return posts


@router.get('/{post_id}', response_model=PostResponse)
async def get_post(post_id: int,
                   current_user: User = Depends(get_current_user),
                   db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))

    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост с данным id не найден")

    res = await db.execute(select(User).where(User.id == post.user_id))

    post.user = res.scalar_one_or_none()

    return post


@router.get('/users/{user_id}', response_model=List[PostResponse])
async def get_user_posts(user_id: int,
                         page: int = 1,
                         size: int = 10,
                         current_user: Optional[User] = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    total_posts = await db.scalar(select(func.count(Post.id)).where(Post.user_id == user_id))

    result = await (db.execute(select(Post)
                               .where(Post.user_id == user_id)
                               .order_by(Post.created_at.desc())
                               .offset((page - 1) * size)
                               .limit(size)))

    posts = result.scalars().all()

    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Этот пользователь еще не выложил ни одного поста")


    res = await db.execute(select(User).where(User.id == user_id))

    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такого пользователя нет")

    for post in posts:
        post.user = user

    return posts
