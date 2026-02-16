from fastapi import APIRouter, Depends
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Post

