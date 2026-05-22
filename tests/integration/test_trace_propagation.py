def test_trace_propagation_e2e(gateway_client):
    response = gateway_client.post(
        "/events",
        json={
            "eventId": "evt-trace-e2e",
            "accountId": "acct-trace",
            "type": "CREDIT",
            "amount": 5,
            "currency": "USD",
            "eventTimestamp": "2026-05-15T14:02:11Z",
        },
        headers={"X-Trace-Id": "e2e-trace-123"},
    )
    assert response.status_code == 201
    assert response.headers.get("X-Trace-Id") == "e2e-trace-123"
