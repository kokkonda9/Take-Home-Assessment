import respx
from httpx import Response


def test_account_failure_returns_503(client):
    with respx.mock(base_url="http://127.0.0.1:8081", assert_all_called=False) as mock:
        mock.post(url__regex=r"/accounts/.+/transactions").mock(return_value=Response(500))
        payload = {
            "eventId": "evt-fail",
            "accountId": "acct-1",
            "type": "CREDIT",
            "amount": 10,
            "currency": "USD",
            "eventTimestamp": "2026-05-15T10:00:00Z",
        }
        response = client.post("/events", json=payload)
        assert response.status_code == 503

    # GET still works when account is down
    stored = client.get("/events/evt-fail")
    assert stored.status_code == 200
