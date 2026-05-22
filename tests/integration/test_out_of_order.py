from decimal import Decimal


def test_out_of_order_events_and_balance(gateway_client, account_client):
    events = [
        ("evt-c", "2026-05-15T12:00:00Z", 30),
        ("evt-a", "2026-05-15T10:00:00Z", 10),
        ("evt-b", "2026-05-15T11:00:00Z", 20),
    ]
    for eid, ts, amount in events:
        r = gateway_client.post("/events", json={
            "eventId": eid,
            "accountId": "acct-order",
            "type": "CREDIT",
            "amount": amount,
            "currency": "USD",
            "eventTimestamp": ts,
        })
        assert r.status_code == 201

    listing = gateway_client.get("/events", params={"account": "acct-order"})
    assert [e["eventId"] for e in listing.json()] == ["evt-a", "evt-b", "evt-c"]

    balance = account_client.get("/accounts/acct-order/balance").json()["balance"]
    assert Decimal(balance) == Decimal("60.00")
