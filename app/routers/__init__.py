from fastapi import APIRouter

from . import login, users, images, groups, expenses, transactions

router = APIRouter()
router.include_router(login.router)
router.include_router(users.router)
router.include_router(images.router)
router.include_router(groups.router)
router.include_router(expenses.router)
router.include_router(transactions.router)
