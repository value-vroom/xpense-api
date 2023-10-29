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
        # If end date is in the past, set status to "Completed"
        if booking.end_date < datetime.now(timezone.utc):
            booking.status_name = "Completed"
            db.booking.update(
                where={
                    "id": booking.id,
                },
                data={
                    "status_name": "Completed",
                },
            )
            continue

        # Check if booking is active
        if booking.start_date < datetime.now(timezone.utc) and booking.end_date > datetime.now(timezone.utc):
            booking.status_name = "Pending"
            db.booking.update(
                where={
                    "id": booking.id,
                },
                data={
                    "status_name": "Pending",
                },
            )

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
        if booking.status_name == "Completed":
            continue
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


# Cancel a booking for the current user
@router.post("/bookings/{booking_id}/cancel", summary="Cancel Booking", response_model_exclude_none=True)
def cancel_booking(
    booking_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Booking:
    """Cancel a booking"""
    db = get_client()
    booking = db.booking.find_first(
        where={
            "id": booking_id,
        },
    )

    if booking is None:
        raise Exception("Booking not found")

    if booking.username != current_user.username:
        raise Exception("Booking not found")

    if booking.status_name != "Booked" and booking.status_name != "Pending":
        raise Exception("Booking is not active")

    db.booking.update(
        where={
            "id": booking_id,
        },
        data={
            "status_name": "Completed",
        },
    )

    return db.booking.find_first(
        where={
            "id": booking_id,
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


# Cancel a booking for the current user
@router.post("/bookings/{booking_id}/activate", summary="Activate Booking", response_model_exclude_none=True)
def activate_booking(
    booking_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Booking:
    """Activate a booking"""
    db = get_client()
    booking = db.booking.find_first(
        where={
            "id": booking_id,
        },
    )

    if booking is None:
        raise Exception("Booking not found")

    if booking.username != current_user.username:
        raise Exception("Booking not found")

    if booking.status_name != "Pending":
        raise Exception("Booking is not pending")

    db.booking.update(
        where={
            "id": booking_id,
        },
        data={
            "status_name": "Active",
        },
    )

    return db.booking.find_first(
        where={
            "id": booking_id,
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
