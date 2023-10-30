"""This router is used to get the reviews"""
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from prisma.models import User, Review

from app.utility.security import get_current_user
from prisma import get_client

router = APIRouter(tags=["Reviews"])


@router.post("/reviews", operation_id="create_review")
def create_review(
    rating: Annotated[float, Form()],
    review: Annotated[str, Form()],
    car_id: Annotated[int, Form()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Create a new review"""
    db = get_client()

    # Ensure rating is between 1 and 5
    if rating < 1 or rating > 5:
        raise Exception("Rating must be between 1 and 5")

    review = db.review.create(
        data={
            "rating": rating,
            "comment": review,
            "car_id": car_id,
            "username": current_user.username,
        },
        include={
            "car": {
                "include": {
                    "car_model": {
                        "include": {
                            "brand": True,
                        },
                    },
                },
            },
            "user": True,
        },
    )

    # Update the car rating
    reviews = db.review.find_many(
        where={
            "car": {
                "id": car_id,
            },
        },
    )
    total_rating = 0
    for review in reviews:
        total_rating += review.rating
    car_rating = total_rating / len(reviews)
    db.car.update(
        where={
            "id": car_id,
        },
        data={
            "rating": car_rating,
        },
    )

    return review
