"""This router is used to handle login and signup"""
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from prisma.models import Token, User
from app.utility.security import authenticate_user, create_access_token, get_password_hash, get_current_user
from prisma import get_client

router = APIRouter(tags=["Login"])


@router.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Login for access token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")  # noqa: S106


@router.post("/signup")
def signup(
    username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    full_name: Annotated[str, Form()],
    password: Annotated[str, Form()],
    profile_image: Annotated[str, Form()],
) -> Token:
    """Signup for access token"""
    db = get_client()

    db.user.create(
        {
            "username": username,
            "email": email,
            "full_name": full_name,
            "hashed_password": get_password_hash(password),
            "profile_image": profile_image,
        },
    )

    access_token = create_access_token(data={"sub": username})

    return Token(
        access_token=access_token,
        token_type="bearer",  # noqa: S106
    )


# Support updating the user's profile data
@router.put("/users/{username}")
def update_user(  # noqa: PLR0913
    username: str,
    email: Annotated[str, Form()],
    full_name: Annotated[str, Form()],
    password: Annotated[str, Form()],
    profile_image: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Update a user's profile data"""
    db = get_client()

    # Check if the current user is the same as the user being updated
    if current_user.username != username:
        raise Exception("You can only update your own profile")

    db.user.update(
        where={"username": username},
        data={
            "email": email,
            "full_name": full_name,
            "hashed_password": get_password_hash(password),
            "profile_image_name": profile_image,
        },
    )

    return db.user.find_first(where={"username": username})
