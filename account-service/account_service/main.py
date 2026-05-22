from contextlib import asynccontextmanager

from fastapi import FastAPI

from account_service.config import settings
from account_service.db import init_db
from account_service.logging_config import setup_logging
from account_service.middleware.trace import TraceMiddleware
from account_service.routers import accounts, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.service_name)
    init_db()
    yield


app = FastAPI(title="Account Service", lifespan=lifespan)
app.add_middleware(TraceMiddleware)
app.include_router(health.router)
app.include_router(accounts.router)
