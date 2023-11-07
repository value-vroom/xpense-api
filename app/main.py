"""FastAPI main module"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import routers
from app.utility.setup_db import register_prisma

app = FastAPI(
    title="XPense API",
    description="This is the API for XPense",
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


@app.exception_handler(Exception)
async def prisma_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Handle Prisma exceptions"""
    return JSONResponse(str(exc), status_code=400)
