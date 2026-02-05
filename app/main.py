from fastapi import FastAPI
import os

from models import Post

app = FastAPI(title="Social API",
              version="0.1.0",)

@app.get("/")
async def health():
    return {"status": "ok"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
