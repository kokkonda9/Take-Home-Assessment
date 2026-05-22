from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class TransactionRequest(BaseModel):
    eventId: str = Field(min_length=1)
    type: Literal["CREDIT", "DEBIT"]
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=1)
    eventTimestamp: datetime
    metadata: dict[str, Any] | None = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class TransactionResponse(BaseModel):
    eventId: str
    accountId: str
    type: str
    amount: Decimal
    currency: str
    eventTimestamp: datetime
    appliedAt: datetime
    metadata: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class BalanceResponse(BaseModel):
    accountId: str
    balance: Decimal
    currency: str = "USD"


class AccountResponse(BaseModel):
    accountId: str
    balance: Decimal
    transactions: list[TransactionResponse]


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str
    timestamp: datetime
