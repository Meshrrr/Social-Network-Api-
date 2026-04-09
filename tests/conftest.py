import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (AsyncEngine,
                                    create_async_engine,
                                    async_sessionmaker,
                                    AsyncSession)

from app.database import get_db, Base
from app.main import app

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

async_test_engine = create_async_engine(DATABASE_URL,)

async_test_session = async_sessionmaker(async_test_engine,
                                        class_=AsyncSession,
                                        expire_on_commit=False
                                        )


async def get_test_db() -> AsyncSession:
    async with async_test_session() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_db] = get_test_db


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
async def setup_db():
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture()
async def db_session() -> AsyncSession:
    async with async_test_session() as session:
        try:
            yield session
        finally:
            await session.close()