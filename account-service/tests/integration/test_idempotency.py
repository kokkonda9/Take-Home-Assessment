from decimal import Decimal


def test_duplicate_event_id_does_not_change_balance(client):
    payload = {
        "eventId": "evt-dup",
        "type": "CREDIT",
        "amount": 100,
        "currency": "USD",
        "eventTimestamp": "2026-05-15T14:02:11Z",
    }
    first = client.post("/accounts/acct-dup/transactions", json=payload)
    second = client.post("/accounts/acct-dup/transactions", json=payload)
    assert first.status_code == 201
    assert second.status_code == 200
    balance = client.get("/accounts/acct-dup/balance").json()["balance"]
    assert Decimal(balance) == Decimal("100.00")
