from enum import Enum
from sqlalchemy import Enum as sql_enum
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
    following = relationship(
        "Follows",
        foreign_keys="Follows.follower_id",
        back_populates="follower")
    followers = relationship(
        "Follows",
        foreign_keys="Follows.following_id",
        back_populates="following")

    notifications = relationship("Notification", foreign_keys="Notification.user_id", back_populates="user")


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
        "Comments",
        back_populates="replies",
        remote_side=[id],
    )

    # Ответы на этот комментарий
    replies = relationship(
        "Comments",
        back_populates="parent",
    )

class Follows(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")

    following = relationship("User", foreign_keys=[following_id], back_populates='followers')



class NotificationType(Enum):
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    REPLY = "reply"



class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    actor_id = Column(Integer, ForeignKey("users.id"), index=True)

    notify_type = Column(sql_enum(NotificationType))

    object_id = Column(Integer)

    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")

    actor = relationship("User", foreign_keys=[actor_id])