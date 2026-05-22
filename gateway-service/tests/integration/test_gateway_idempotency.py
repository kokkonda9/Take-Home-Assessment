def test_duplicate_event_returns_200(client, mock_account_ok):
    payload = {
        "eventId": "evt-dup",
        "accountId": "acct-1",
        "type": "CREDIT",
        "amount": 50,
        "currency": "USD",
        "eventTimestamp": "2026-05-15T10:00:00Z",
    }
    first = client.post("/events", json=payload)
    second = client.post("/events", json=payload)
    assert first.status_code == 201
    assert second.status_code == 200
    assert mock_account_ok.calls.call_count == 1
