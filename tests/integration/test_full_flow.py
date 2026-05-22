from decimal import Decimal


def test_full_flow(gateway_client, account_client):
    payload = {
        "eventId": "evt-e2e-001",
        "accountId": "acct-e2e",
        "type": "CREDIT",
        "amount": 150.00,
        "currency": "USD",
        "eventTimestamp": "2026-05-15T14:02:11Z",
        "metadata": {"source": "e2e-test"},
    }
    create = gateway_client.post("/events", json=payload)
    assert create.status_code == 201

    fetched = gateway_client.get("/events/evt-e2e-001")
    assert fetched.status_code == 200
    assert fetched.json()["eventId"] == "evt-e2e-001"

    balance = account_client.get("/accounts/acct-e2e/balance")
    assert balance.status_code == 200
    assert Decimal(balance.json()["balance"]) == Decimal("150.00")
