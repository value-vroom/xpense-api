"""This router is used to get the cars"""
from fastapi import APIRouter, Depends
from prisma.models import Car, User, Booking, Review
from datetime import datetime, timezone
from prisma import get_client
from typing import Annotated
from app.utility.security import get_current_user

router = APIRouter(tags=["Cars"])


# Get all cars
@router.get("/cars/all", operation_id="get_all_cars", response_model_exclude_none=True)
def get_all_cars() -> list[Car]:
    """Get all cars"""
    db = get_client()
    return db.car.find_many(
        include={
            "car_model": {
                "include": {
                    "brand": True,
                },
            },
        },
    )


# Get booked cars
@router.get("/cars/booked", operation_id="get_booked_cars", response_model_exclude_none=True)
def get_booked_cars(current_user: Annotated[User, Depends(get_current_user)]) -> list[Car]:
    """Get all booked cars"""
    db = get_client()
    cars = get_all_cars()
    booked_cars = []
    for car in cars:
        bookings = db.booking.find_many(
            where={
                "car": {
                    "id": car.id,
                },
                "user": {
                    "username": current_user.username,
                },
                "status": {
                    "name": "Booked",
                },
            },
        )
        if len(bookings) > 0:
            car_booked = False
            for booking in bookings:
                if booking.start_date < datetime.now(timezone.utc) and booking.end_date > datetime.now(
                    timezone.utc,
                ):
                    car_booked = True
                    break
            if car_booked:
                booked_cars.append(car)
    return booked_cars


# Get avaliable cars
@router.get("/cars/available", operation_id="get_available_cars", response_model_exclude_none=True)
def get_available_cars() -> list[Car]:
    """Get all available cars"""
    db = get_client()
    cars = get_all_cars()
    available_cars = []
    for car in cars:
        bookings = db.booking.find_many(
            where={
                "car": {
                    "id": car.id,
                },
            },
        )
        if len(bookings) == 0:
            available_cars.append(car)
        else:
            car_booked = False
            for booking in bookings:
                if booking.status_name in ("Completed", "Cancelled"):
                    continue
                if booking.start_date < datetime.now(timezone.utc) and booking.end_date > datetime.now(
                    timezone.utc,
                ):
                    car_booked = True
                    break
            if not car_booked:
                available_cars.append(car)
    return available_cars


# Get all bookings for a specific car
@router.get("/cars/{car_id}/bookings", operation_id="get_car_bookings", response_model_exclude_none=True)
def get_car_bookings(car_id: int) -> list[Booking]:
    """Get all bookings for a specific car"""
    db = get_client()
    return db.booking.find_many(
        where={
            "car": {
                "id": car_id,
            },
        },
    )


# Get all reviews for a specific car
@router.get("/cars/{car_id}/reviews", operation_id="get_car_reviews", response_model_exclude_none=True)
def get_car_reviews(car_id: int) -> list[Review]:
    """Get all reviews for a specific car"""
    db = get_client()
    return db.review.find_many(
        where={
            "car": {
                "id": car_id,
            },
        },
        include={
            "user": True,
        },
    )
