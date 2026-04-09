import pytest

from app.models import User, Follows, Post, Like, Notification
from app.database import Base
from app.api.v1.utils.auth.auth_utils import hash_password, encode_jwt
from tests.conftest import client


@pytest.mark.asyncio
async def test_create_post(db_session, client):
    #Arrange
    hashed_pwd = hash_password("123123")
    user = User(
        username="test",
        email="test@example.com",
        hashed_password=hashed_pwd
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "username": user.username,
    }

    access_token = encode_jwt(payload=token_payload)



    #Act
    response = client.post(
        "/api/v1/posts/",
        json={
            "body": "Testing",
            "user_id": user.id
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )

    #Assert

    assert response.status_code == 201
    assert response.json()["user_id"] == user.id
    assert response.json()["body"] == "Testing"
    assert response.json()["likes_count"] == 0
    assert response.json()["comments_count"] == 0


