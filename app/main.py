from fastapi import FastAPI, Depends, HTTPException, status
import os
from auth.auth_utils import router as auth_router
from app.database import create_tables
from app.database import get_db
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

app = FastAPI(title="Social API",
              version="0.1.0",)

app.include_router(auth_router)

@app.on_event("startup")
async def on_startup():
    await create_tables()
    print("✅ Database tables initialized")


@app.get("/")
async def health():
    return {"status": "ok"}

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(Select(User))

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователи отсутствуют")
    else:
        return result

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
