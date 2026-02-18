from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Post, User
from app.schemas import Post, PostUpdate, PostResponse, UserShortInfo
from app.auth.auth_utils import get_current_user
router = APIRouter(prefix="/posts", tags=["posts"])

@router.post('/', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: Post, current_user: User = Depends(get_current_user),
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


@router.get('/users/{user_id}', response_model=PostResponse)
async def get_user_posts(user_id: int,
                         current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    pass




#реализовать ленту потом
@router.get('/feed')
async def get_feed():
    pass