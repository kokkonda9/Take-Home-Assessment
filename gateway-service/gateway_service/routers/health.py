from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from gateway_service.config import settings
from gateway_service.db import check_db_connection
from gateway_service.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    db_ok = check_db_connection()
    body = HealthResponse(
        status="UP" if db_ok else "DOWN",
        service=settings.service_name,
        database="UP" if db_ok else "DOWN",
        timestamp=datetime.now(timezone.utc),
    )
    if not db_ok:
        return JSONResponse(status_code=503, content=body.model_dump(mode="json"))
    return body
