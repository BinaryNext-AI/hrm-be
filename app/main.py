from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from .db import init_pool
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="HRM Backend - MySQL Connector")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    return app


app = create_app()


