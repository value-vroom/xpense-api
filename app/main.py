"""FastAPI main module"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prisma.errors import DataError

from app import routers
from app.utility.setup_db import register_prisma

app = FastAPI(
    title="ValueVroom API",
    description="This is the API for ValueVroom",
)
app.include_router(routers.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_prisma()


@app.exception_handler(DataError)
async def prisma_exception_handler(_: Request, exc: DataError) -> JSONResponse:
    """Handle Prisma exceptions"""
    return JSONResponse(str(exc), status_code=400)
