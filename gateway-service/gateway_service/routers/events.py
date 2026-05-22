from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from gateway_service.db import get_db
from gateway_service.metrics import metrics
from gateway_service.schemas import EventRequest, EventResponse
from gateway_service.services.event_service import create_event, get_event, list_events

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse)
async def post_event(
    payload: EventRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    trace_id = getattr(request.state, "trace_id", None)
    result, status_code = await create_event(db, payload, trace_id)
    metrics.record_event("POST /events", str(status_code))
    if status_code == 201:
        return JSONResponse(status_code=201, content=result.model_dump(mode="json"))
    return result


@router.get("/{event_id}", response_model=EventResponse)
def get_event_by_id(event_id: str, db: Session = Depends(get_db)):
    return get_event(db, event_id)


@router.get("", response_model=list[EventResponse])
def get_events_by_account(account: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return list_events(db, account)
