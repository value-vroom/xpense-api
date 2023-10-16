"""This router is used to get the cars"""
from fastapi import APIRouter
from prisma.models import Car

from prisma import get_client

router = APIRouter(tags=["Cars"])


@router.get("/cars", summary="Get Cars", response_model_exclude_none=True)
def get_cars() -> list[Car]:
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
