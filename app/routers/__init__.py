from fastapi import APIRouter

from . import cars, login, users, images, bookings

router = APIRouter()
router.include_router(login.router)
router.include_router(users.router)
router.include_router(cars.router)
router.include_router(images.router)
router.include_router(bookings.router)
