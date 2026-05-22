import respx
from httpx import Response


def test_get_event_by_id(client, mock_account_ok):
    payload = {
        "eventId": "evt-get",
        "accountId": "acct-1",
        "type": "CREDIT",
        "amount": 10,
        "currency": "USD",
        "eventTimestamp": "2026-05-15T10:00:00Z",
    }
    client.post("/events", json=payload)
    response = client.get("/events/evt-get")
    assert response.status_code == 200
    assert response.json()["eventId"] == "evt-get"


def test_list_events_chronological(client):
    with respx.mock(base_url="http://127.0.0.1:8081", assert_all_called=False) as mock:
        mock.post(url__regex=r"/accounts/.+/transactions").mock(return_value=Response(201, json={}))

        client.post("/events", json={
            "eventId": "evt-c", "accountId": "acct-1", "type": "CREDIT", "amount": 30,
            "currency": "USD", "eventTimestamp": "2026-05-15T12:00:00Z",
        })
        client.post("/events", json={
            "eventId": "evt-a", "accountId": "acct-1", "type": "CREDIT", "amount": 10,
            "currency": "USD", "eventTimestamp": "2026-05-15T10:00:00Z",
        })

    response = client.get("/events", params={"account": "acct-1"})
    assert response.status_code == 200
    ids = [e["eventId"] for e in response.json()]
    assert ids == ["evt-a", "evt-c"]
