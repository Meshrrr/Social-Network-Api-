from typing import Optional

from fastapi import HTTPException, APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Post, User, Comments
from app.schemas.comments_schemas import CommentsResponse, CommentCreate
from app.auth.auth_utils import get_current_user

router = APIRouter(prefix="/posts", tags=["comments"])

@router.post("/{post_id}/comments", response_model=CommentsResponse)
async def create_comment(content: CommentCreate,
                         post_id: int,
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    current_post = result.scalar_one_or_none()

    if not current_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    if content.parent_id:
        result = await db.execute(select(Comments).where(Comments.id == content.parent_id,
                                                        Comments.post_id == post_id))
        parent = result.scalar_one_or_none()

        if not parent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Родительский комментарий не найден")

    comment = Comments(
        content=content.content,
        user_id=user.id,
        post_id=post_id,
        parent_id=content.parent_id
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    result = await db.execute(
        select(Comments)
        .where(Comments.id == comment.id)
        .options(selectinload(Comments.user))
    )
    comment = result.scalar_one()

    comment.is_owner = True

    return comment

@router.get("/comments/{comment_id}", response_model=CommentsResponse)
async def get_comment_by_id(comment_id: int,
                            current_user: Optional[User] = Depends(get_current_user),
                            db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comments)
                              .where(Comments.id == comment_id)
                              .options(selectinload(Comments.user), selectinload(Comments.replies).selectinload(Comments.user)))

    current_comment = result.scalar_one_or_none()

    if not current_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий с таким id не найден")

    current_comment.is_owner = current_user and current_user.id == current_comment.user_id

    for reply in current_comment.replies:
        reply.is_owner = current_user and current_user.id == reply.user_id


    current_comment.replies_count = len(current_comment.replies)

    return current_comment

@router.patch("/comments/{comment_id}", response_model= CommentsResponse)
async def update_comment(comment_id: int,
                         content: str,
                         current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comments).where(Comments.id == comment_id))

    current_comment = result.scalar_one_or_none()

    if not current_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий с таким id не найден")

    if current_user.id != current_comment.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Вы не можете редактировать чужой комментарий")

    current_comment.content = content

    await db.commit()
    await db.refresh(current_comment)

    current_comment.is_owner = True

    return current_comment




#проверить почему не показывает кол-во ответов на коммент

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int,
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Comments).where(Comments.id == comment_id))

    current_comment = result.scalar_one_or_none()

    if not current_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден")

    if user.id != current_comment.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нельзя изменять чужой комментарий!")

    await db.delete(current_comment)
    await db.commit()

    return {
        "message": "Комментарий удален"
    }


