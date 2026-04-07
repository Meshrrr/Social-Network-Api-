from fastapi import FastAPI
from app.database import create_tables

from app.auth.auth_utils import router as auth_router
from app.users.user_utils import router as users_router
from app.posts.posts import router as posts_router
from app.posts.likes_utils import router as likes_router
from app.posts.comments_utils import router as comments_router
from app.users.subscribes_utils import router as subscribes_router
from app.posts.following_feed import router as following_feed


app = FastAPI(title="Social API",
              version="1.0.0",)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(posts_router)
app.include_router(likes_router)
app.include_router(comments_router)
app.include_router(subscribes_router)
app.include_router(following_feed)

@app.on_event("startup")
async def on_startup():
    await create_tables()
    print("✅ Database tables initialized")


@app.get("/")
async def health():
    return {"status": "ok"}
