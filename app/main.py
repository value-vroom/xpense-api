"""FastAPI main module"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prisma.errors import DataError

from app import routers
from app.utility.setup_db import setup_db

app = FastAPI(
    title="ValueVroom API",
    description="This is the API for ValueVroom",
)
app.include_router(routers.router)

setup_db()


@app.exception_handler(DataError)
async def prisma_exception_handler(_: Request, exc: DataError) -> JSONResponse:
    """Handle Prisma exceptions"""
    return JSONResponse(str(exc), status_code=400)
