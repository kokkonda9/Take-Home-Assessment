from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from account_service.db import get_db
from account_service.schemas import AccountResponse, BalanceResponse, TransactionRequest, TransactionResponse
from account_service.services.transaction_service import apply_transaction, get_account_details, get_balance

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/{account_id}/transactions")
def post_transaction(account_id: str, payload: TransactionRequest, db: Session = Depends(get_db)):
    result, created = apply_transaction(db, account_id, payload)
    if created:
        return JSONResponse(status_code=201, content=result.model_dump(mode="json"))
    return result


@router.get("/{account_id}/balance", response_model=BalanceResponse)
def account_balance(account_id: str, db: Session = Depends(get_db)):
    balance = get_balance(db, account_id)
    return BalanceResponse(accountId=account_id, balance=balance)


@router.get("/{account_id}", response_model=AccountResponse)
def account_details(account_id: str, db: Session = Depends(get_db)):
    balance, txns = get_account_details(db, account_id)
    return AccountResponse(
        accountId=account_id,
        balance=balance,
        transactions=[TransactionResponse(
            eventId=t.event_id,
            accountId=t.account_id,
            type=t.type,
            amount=t.amount,
            currency=t.currency,
            eventTimestamp=t.event_timestamp,
            appliedAt=t.applied_at,
        ) for t in txns],
    )
