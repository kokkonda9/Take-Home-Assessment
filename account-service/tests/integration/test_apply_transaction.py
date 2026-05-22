from decimal import Decimal


def _payload(event_id="evt-001", type_="CREDIT", amount="150.00"):
    return {
        "eventId": event_id,
        "type": type_,
        "amount": amount,
        "currency": "USD",
        "eventTimestamp": "2026-05-15T14:02:11Z",
    }


def test_apply_credit_creates_account(client):
    response = client.post("/accounts/acct-123/transactions", json=_payload())
    assert response.status_code == 201
    assert response.json()["eventId"] == "evt-001"


def test_apply_debit_updates_balance(client):
    client.post("/accounts/acct-123/transactions", json=_payload("evt-001", "CREDIT", "150.00"))
    client.post("/accounts/acct-123/transactions", json=_payload("evt-002", "DEBIT", "50.00"))
    balance = client.get("/accounts/acct-123/balance")
    assert balance.status_code == 200
    assert Decimal(balance.json()["balance"]) == Decimal("100.00")
