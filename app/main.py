from fastapi import FastAPI, Depends, HTTPException, status
import os
from app.auth.auth_utils import get_current_user
from app.database import create_tables
from app.database import get_db
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.schemas.user_schemas import UserResponse

from app.auth.auth_utils import router as auth_router
from app.users.user_utils import router as users_router
from app.posts.posts import router as posts_router
from app.posts.likes_utils import router as likes_router


app = FastAPI(title="Social API",
              version="0.1.0",)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(posts_router)
app.include_router(likes_router)

@app.on_event("startup")
async def on_startup():
    await create_tables()
    print("✅ Database tables initialized")


@app.get("/")
async def health():
    return {"status": "ok"}
