from fastapi import FastAPI
import os
from auth.auth_utils import router as auth_router
from app.database import create_tables

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


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
