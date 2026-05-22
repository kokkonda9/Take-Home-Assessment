def test_post_event_calls_account(client, mock_account_ok):
    payload = {
        "eventId": "evt-001",
        "accountId": "acct-123",
        "type": "CREDIT",
        "amount": 150.00,
        "currency": "USD",
        "eventTimestamp": "2026-05-15T14:02:11Z",
    }
    response = client.post("/events", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "APPLIED"
    assert mock_account_ok.calls.call_count == 1
