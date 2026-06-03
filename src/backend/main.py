from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from backend.database import init_db
from backend.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


def create_app(init_database: bool = True) -> FastAPI:
    app = FastAPI(title="MyApp Backend", lifespan=lifespan if init_database else None)
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    return app


app = create_app()
