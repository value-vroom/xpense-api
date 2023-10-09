from fastapi import APIRouter

from . import cars, login, users

router = APIRouter()
router.include_router(login.router)
router.include_router(users.router)
router.include_router(cars.router)
