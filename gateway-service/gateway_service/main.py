from contextlib import asynccontextmanager

from fastapi import FastAPI

from gateway_service.config import settings
from gateway_service.db import init_db
from gateway_service.logging_config import setup_logging
from gateway_service.middleware.trace import TraceMiddleware
from gateway_service.routers import events, health, metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.service_name)
    init_db()
    yield


app = FastAPI(title="Event Gateway", lifespan=lifespan)
app.add_middleware(TraceMiddleware)
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(events.router)
