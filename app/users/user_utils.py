from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.schemas import UserResponse
from auth.auth_utils import get_current_user
from app.database import Base, get_db

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(Select(User))
    users = result.scalars().all()

    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователи отсутствуют")
    else:
        return users

@router.get("/users/{user_id}")
async def get_user(user_id: int,
                   db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))

    user_result = result.scalar_one_or_none()
    if user_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: '{user_id}' not found")

@router.patch("/me/update/", response_model=UserResponse)
async def update_user( db: AsyncSession = Depends(get_db)):
 pass