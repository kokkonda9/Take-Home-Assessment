from datetime import datetime, timezone
from decimal import Decimal

import structlog
from fastapi import HTTPException
from sqlalchemy.orm import Session

from account_service.models import Account, Transaction
from account_service.schemas import TransactionRequest, TransactionResponse

logger = structlog.get_logger()


def _to_response(txn: Transaction) -> TransactionResponse:
    return TransactionResponse(
        eventId=txn.event_id,
        accountId=txn.account_id,
        type=txn.type,
        amount=txn.amount,
        currency=txn.currency,
        eventTimestamp=txn.event_timestamp,
        appliedAt=txn.applied_at,
        metadata=None,
    )


def apply_transaction(
    db: Session, account_id: str, payload: TransactionRequest
) -> tuple[TransactionResponse, bool]:
    existing = db.query(Transaction).filter(Transaction.event_id == payload.eventId).first()
    if existing:
        logger.info("duplicate_transaction", event_id=payload.eventId)
        return _to_response(existing), False

    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        account = Account(account_id=account_id, balance=Decimal("0.00"))
        db.add(account)
        db.flush()

    delta = payload.amount if payload.type == "CREDIT" else -payload.amount
    account.balance = Decimal(str(account.balance)) + delta

    txn = Transaction(
        event_id=payload.eventId,
        account_id=account_id,
        type=payload.type,
        amount=payload.amount,
        currency=payload.currency,
        event_timestamp=payload.eventTimestamp,
        applied_at=datetime.now(timezone.utc),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    logger.info("transaction_applied", event_id=payload.eventId, account_id=account_id, balance=str(account.balance))
    return _to_response(txn), True


def get_balance(db: Session, account_id: str) -> Decimal:
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    return Decimal(str(account.balance))


def get_account_details(db: Session, account_id: str) -> tuple[Decimal, list[Transaction]]:
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    txns = (
        db.query(Transaction)
        .filter(Transaction.account_id == account_id)
        .order_by(Transaction.event_timestamp.asc(), Transaction.event_id.asc())
        .all()
    )
    return Decimal(str(account.balance)), txns
