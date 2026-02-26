from fastapi import HTTPException, APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Post, User, Comments
from app.schemas.comments_schemas import CommentsBase, CommentsResponse
from app.auth.auth_utils import get_current_user

router = APIRouter(prefix="/posts", tags=["comments"])

@router.post("/{post_id}/comments", response_model=CommentsResponse)
async def create_comment(content: str,
                         post_id: int,
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db())):
    result = await db.execute(select(Post).where(Post.id == post_id))
    current_post = result.scalar_one_or_none()

    if not current_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

