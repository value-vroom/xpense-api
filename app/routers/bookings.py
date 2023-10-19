"""This router is used to manage the bookings"""
from fastapi import APIRouter, Depends, Form
from prisma.models import Booking, User
from app.utility.security import get_current_user
from typing import Annotated
from datetime import datetime, timezone
from prisma import get_client

router = APIRouter(tags=["Bookings"])


# Get all bookings for the current user
@router.get("/bookings", summary="Get Bookings", response_model_exclude_none=True)
def get_bookings(current_user: Annotated[User, Depends(get_current_user)]) -> list[Booking]:
    """Get all bookings"""
    db = get_client()
    bookings = db.booking.find_many(
        where={
            "user": {
                "username": current_user.username,
            },
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
            "status": True,
        },
    )

    for booking in bookings:
        if booking.status_name != "Booked":
            continue
        # Check if booking is active
        if booking.start_date < datetime.now(timezone.utc) and booking.end_date > datetime.now(timezone.utc):
            booking.status_name = "Pending"

    return bookings


# Create a booking for the current user
@router.post("/bookings", summary="Create Booking", response_model_exclude_none=True)
def create_booking(
    end_date: Annotated[datetime, Form()],
    car_id: Annotated[int, Form()],
    current_user: Annotated[User, Depends(get_current_user)],
    start_date: Annotated[datetime | None, Form()] = None,
) -> Booking:
    """Create a booking"""
    db = get_client()

    if start_date is not None and start_date.astimezone(timezone.utc) < datetime.now(timezone.utc):
        raise Exception("Start date must be in the future")

    start_date = datetime.now(timezone.utc) if start_date is None else start_date

    # Validate that the start date is before the end date and that the start date is in the future
    if start_date.astimezone(timezone.utc) >= end_date.astimezone(timezone.utc):
        raise Exception("Start date must be before end date")

    # Validate that the car is available
    bookings = db.booking.find_many(
        where={
            "car": {
                "id": car_id,
            },
        },
    )

    for booking in bookings:
        if booking.start_date.astimezone(timezone.utc) < start_date.astimezone(
            timezone.utc,
        ) < booking.end_date.astimezone(timezone.utc) or booking.start_date.astimezone(
            timezone.utc,
        ) < end_date.astimezone(
            timezone.utc,
        ) < booking.end_date.astimezone(
            timezone.utc,
        ):
            raise Exception("Car is not available")

    return db.booking.create(
        {
            "start_date": start_date,
            "end_date": end_date,
            "username": current_user.username,
            "car_id": car_id,
            "status_name": "Booked",
        },
    )
