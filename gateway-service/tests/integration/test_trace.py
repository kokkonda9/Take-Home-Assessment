def test_trace_header_on_response(client, mock_account_ok):
    payload = {
        "eventId": "evt-trace",
        "accountId": "acct-1",
        "type": "CREDIT",
        "amount": 10,
        "currency": "USD",
        "eventTimestamp": "2026-05-15T10:00:00Z",
    }
    response = client.post("/events", json=payload, headers={"X-Trace-Id": "trace-abc"})
    assert response.headers.get("X-Trace-Id") == "trace-abc"
    assert mock_account_ok.calls.last.request.headers["X-Trace-Id"] == "trace-abc"
