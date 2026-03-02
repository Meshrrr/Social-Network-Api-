from fastapi import HTTPException, APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Post, User, Comments
from app.schemas.comments_schemas import CommentsBase, CommentsResponse, CommentCreate
from app.auth.auth_utils import get_current_user

router = APIRouter(prefix="/posts", tags=["comments"])

@router.post("/{post_id}/comments", response_model=CommentsResponse)
async def create_comment(content: CommentCreate,
                         post_id: int,
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db())):
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

    return comment

#сделать получения коммента по айди(с ответами), апдейт коммента

@router.post("/comments/{comment_id}")
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


