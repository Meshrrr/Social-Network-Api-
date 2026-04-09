import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import *
from app.api.v1.utils.auth.auth_utils import hash_password, encode_jwt
from tests.conftest import client

async def create_test_user(password: str, username: str, email: str):
    hashed_pwd = hash_password(password)

    user = User(
        username=username,
        email=email,
        hashed_password=hashed_pwd,
    )

    return user

@pytest.mark.asyncio
async def test_like_create(client, db_session):
    #Arrange

    user = await create_test_user(password="123123", username="test", email="example@test.ru")

    db_session.add(user)
    await db_session.flush()

    user2 = await create_test_user(password="123123123", username="test2", email="exampl@test.ru")

    db_session.add(user2)
    await db_session.flush()

    user3 = await create_test_user(password="111111", username="test3", email="examp@test.ru")

    db_session.add(user3)
    await db_session.flush()

    user4 = await create_test_user(password="111111111111", username="test4", email="exam@test.ru")

    db_session.add(user4)
    await db_session.flush()


    post = Post(
        body="Testing",
        user_id=user2.id
    )

    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)

    payload_token_user1 = {
        "sub": str(user.id),
        "email":user.email,
        "username": user.username,
    }

    payload_token_user3 = {
        "sub": str(user3.id),
        "email": user3.email,
        "username": user3.username,
    }

    payload_token_user4 = {
        "sub": str(user4.id),
        "email": user4.email,
        "username": user4.username,
    }

    access_token_user1 = encode_jwt(payload=payload_token_user1)
    access_token_user3 = encode_jwt(payload=payload_token_user3)
    access_token_user4 = encode_jwt(payload=payload_token_user4)


    #Act

    response1 = client.post(f"/api/v1/posts/{post.id}/like",
                headers={"Authorization": f"Bearer {access_token_user1}"})

    response2 = client.post(f"/api/v1/posts/{post.id}/like",
                headers={"Authorization": f"Bearer {access_token_user3}"})

    response3 = client.post(f"/api/v1/posts/{post.id}/like",
                headers={"Authorization": f"Bearer {access_token_user4}"})

    result = await db_session.execute(
        select(Post)
        .where(Post.id == post.id)
        .options(selectinload(Post.likes))
    )
    post_result = result.scalar_one()

    get_post = client.get(f"/api/v1/posts/{post.id}",
                          headers={"Authorization": f"Bearer {access_token_user1}"})


    #Assert

    assert response1.status_code == 200
    assert response1.json()["post_id"] == post.id

    assert response2.status_code == 200
    assert response2.json()["post_id"] == post.id

    assert response3.status_code == 200
    assert response3.json()["post_id"] == post.id


    assert get_post.status_code == 200
    assert get_post.json()["likes_count"] == len(post_result.likes)








