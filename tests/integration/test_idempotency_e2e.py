from decimal import Decimal


def test_idempotency_e2e(gateway_client, account_client):
    payload = {
        "eventId": "evt-idem-e2e",
        "accountId": "acct-idem",
        "type": "CREDIT",
        "amount": 75.00,
        "currency": "USD",
        "eventTimestamp": "2026-05-15T14:02:11Z",
    }
    first = gateway_client.post("/events", json=payload)
    second = gateway_client.post("/events", json=payload)
    assert first.status_code == 201
    assert second.status_code == 200

    balance = account_client.get("/accounts/acct-idem/balance").json()["balance"]
    assert Decimal(balance) == Decimal("75.00")
