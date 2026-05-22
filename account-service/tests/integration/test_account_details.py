def test_account_details_sorted_by_timestamp(client):
    client.post("/accounts/acct-1/transactions", json={
        "eventId": "evt-c", "type": "CREDIT", "amount": 30,
        "currency": "USD", "eventTimestamp": "2026-05-15T12:00:00Z",
    })
    client.post("/accounts/acct-1/transactions", json={
        "eventId": "evt-a", "type": "CREDIT", "amount": 10,
        "currency": "USD", "eventTimestamp": "2026-05-15T10:00:00Z",
    })
    response = client.get("/accounts/acct-1")
    assert response.status_code == 200
    ids = [t["eventId"] for t in response.json()["transactions"]]
    assert ids == ["evt-a", "evt-c"]
