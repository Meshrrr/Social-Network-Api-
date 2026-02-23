from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.schemas .user_schemas import UserResponse,UserUpdate, PasswordUpdate
from app.auth.auth_utils import get_current_user, hash_password, valid_password
from app.database import Base, get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(Select(User))
    users = result.scalars().all()

    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователи отсутствуют")
    else:
        return users

@router.get("/{user_id}/", response_model=UserResponse)
async def get_user(user_id: int,
                   db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))

    user_result = result.scalar_one_or_none()
    if not user_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Пользователь с id: '{user_id}' не найден")

    return user_result

@router.patch("/me/update/", response_model=UserResponse)
async def update_user(user_update: UserUpdate,
                      current_user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):

    what_update = []

    if user_update.username is not None and not "String":

        if user_update.username != current_user.username:

            result = await db.execute(select(User).where(User.username == user_update.username,
                                                         User.id != current_user.id))

            existing_user = result.scalar_one_or_none()

            if existing_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Этот юзернейм уже щзанят")

            current_user.username = user_update.username
            what_update.append("username")


    if user_update.email is not None or not "EmailStr":

        if user_update.email != current_user.email:

            result = await db.execute(select(User).where(User.email == user_update.email,
                                                         User.id != current_user.id))

            existing_user = result.scalar_one_or_none()

            if existing_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Этот email уже занят")

            current_user.email = user_update.email
            what_update.append("email")


    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
        what_update.append("full_name")


    if user_update.bio is not None:
        current_user.bio = user_update.bio
        what_update.append("bio")


    if not what_update:
        return {
            "message": "Ничего не было обновлено!"
        }



    await db.commit()
    await db.refresh(current_user)

    return current_user

@router.put("/me/update/password")
async def update_user_password(update_password: PasswordUpdate,
                               current_user: User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):


    if not valid_password(update_password.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail= "Текущий пароль указан неверно")

    if update_password.new_password == update_password.current_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Новый пароль должен отличаться от предыдущего")

    if update_password.confirm_password != update_password.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Новый пароль и подтверждение не совпадают")

    if len(update_password.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Пароль должен содержать не менее 6 символов!")

    hashed_pwd_new = hash_password(update_password.new_password)
    current_user.hashed_password = hashed_pwd_new

    await db.commit()
    await db.refresh(current_user)

    return {
        "message": "Пароль обновлен успешно"
    }

@router.delete("/me/delete/")
async def delete_account(delete_account: bool,
                         current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == current_user.id))
    delete_user = result.scalar_one_or_none()


    if not delete_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вы не авторизованы")


    if delete_account:
        await db.delete(delete_user)
        await db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Можете вернуться на прошлую страницу")


    return {
        "message": "Ваш аккаунт успешно удален"
    }