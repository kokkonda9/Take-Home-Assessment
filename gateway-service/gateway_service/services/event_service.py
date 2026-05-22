import structlog
from fastapi import HTTPException
from sqlalchemy.orm import Session

from gateway_service.clients.account_client import AccountClient, AccountServiceUnavailable
from gateway_service.models import EventRecord, EventStatus
from gateway_service.schemas import EventRequest, EventResponse

logger = structlog.get_logger()


def _to_response(record: EventRecord) -> EventResponse:
    return EventResponse(
        eventId=record.event_id,
        accountId=record.account_id,
        type=record.type,
        amount=record.amount,
        currency=record.currency,
        eventTimestamp=record.event_timestamp,
        metadata=record.metadata_json,
        status=record.status,
        createdAt=record.created_at,
    )


async def create_event(
    db: Session,
    payload: EventRequest,
    trace_id: str,
    account_client: AccountClient | None = None,
) -> tuple[EventResponse, int]:
    existing = db.query(EventRecord).filter(EventRecord.event_id == payload.eventId).first()
    if existing:
        logger.info("duplicate_event", event_id=payload.eventId)
        return _to_response(existing), 200

    record = EventRecord(
        event_id=payload.eventId,
        account_id=payload.accountId,
        type=payload.type,
        amount=payload.amount,
        currency=payload.currency,
        event_timestamp=payload.eventTimestamp,
        metadata_json=payload.metadata,
        status=EventStatus.PENDING.value,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    client = account_client or AccountClient()
    txn_payload = {
        "eventId": payload.eventId,
        "type": payload.type,
        "amount": str(payload.amount),
        "currency": payload.currency,
        "eventTimestamp": payload.eventTimestamp.isoformat(),
        "metadata": payload.metadata,
    }

    try:
        await client.apply_transaction(payload.accountId, txn_payload, trace_id)
    except AccountServiceUnavailable as exc:
        record.status = EventStatus.FAILED.value
        db.commit()
        db.refresh(record)
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "traceId": trace_id},
        ) from exc

    record.status = EventStatus.APPLIED.value
    db.commit()
    db.refresh(record)
    logger.info("event_applied", event_id=payload.eventId)
    return _to_response(record), 201


def get_event(db: Session, event_id: str) -> EventResponse:
    record = db.query(EventRecord).filter(EventRecord.event_id == event_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return _to_response(record)


def list_events(db: Session, account_id: str) -> list[EventResponse]:
    records = (
        db.query(EventRecord)
        .filter(EventRecord.account_id == account_id)
        .order_by(EventRecord.event_timestamp.asc(), EventRecord.event_id.asc())
        .all()
    )
    return [_to_response(r) for r in records]
