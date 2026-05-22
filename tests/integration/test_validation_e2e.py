def test_validation_e2e(gateway_client):
    response = gateway_client.post("/events", json={
        "eventId": "evt-bad",
        "accountId": "acct-1",
        "type": "CREDIT",
        "amount": -5,
        "currency": "USD",
        "eventTimestamp": "2026-05-15T14:02:11Z",
    })
    assert response.status_code == 422
