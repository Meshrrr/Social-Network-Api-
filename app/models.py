from sqlalchemy import Integer, Column, String, ForeignKey, DateTime, Text, Boolean, func
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String)
    full_name = Column(String)
    bio= Column(String, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))

    posts = relationship("Post", back_populates="user")
    likes = relationship("Like", back_populates="user")
    comments = relationship("Comments", back_populates="user")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    body = Column(String, nullable=False)
    image_url = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post")
    comments = relationship("Comments", back_populates="post")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # !!

    user = relationship("User",back_populates="likes")
    post =relationship("Post", back_populates="likes")


#COMMENTS

class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_updated = Column(Boolean, default=False)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    parent = relationship(
        "Comment",
        back_populates="replies",
        remote_side=[id],
    )

    # Ответы на этот комментарий
    replies = relationship(
        "Comment",
        back_populates="parent",
    )
