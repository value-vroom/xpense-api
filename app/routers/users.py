"""This router is used to get the users"""
from typing import Annotated

from fastapi import APIRouter, Depends
from prisma.models import User

from app.utility.security import get_current_user
from prisma import get_client

router = APIRouter(tags=["Users"])


@router.get("/current_user")
def current_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Get the current user"""
    return current_user


@router.get("/users")
def users() -> list[User]:
    """Get all users"""
    db = get_client()
    return db.user.find_many()
