from fastapi import FastAPI
from app.database import create_tables

from api.v1.utils.auth.auth_utils import router as auth_router
from api.v1.utils.user.user_utils import router as users_router
from api.v1.utils.post.posts import router as posts_router
from api.v1.utils.like.likes_utils import router as likes_router
from api.v1.utils.post.comments_utils import router as comments_router
from api.v1.utils.follow.subscribes_utils import router as subscribes_router
from api.v1.utils.follow.following_feed import router as following_feed


app = FastAPI(title="Social API",
              version="1.0.0",)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(likes_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(subscribes_router, prefix="/api/v1")
app.include_router(following_feed, prefix="/api/v1")

@app.on_event("startup")
async def on_startup():
    await create_tables()
    print("Database tables initialized")


@app.get("/")
async def health():
    return {"status": "ok"}
