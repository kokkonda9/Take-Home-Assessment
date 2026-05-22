import pytest


@pytest.mark.parametrize("payload,field", [
    ({"accountId": "a", "type": "CREDIT", "amount": 1, "currency": "USD", "eventTimestamp": "2026-05-15T14:02:11Z"}, "eventId"),
    ({"eventId": "e", "type": "CREDIT", "amount": 1, "currency": "USD", "eventTimestamp": "2026-05-15T14:02:11Z"}, "accountId"),
    ({"eventId": "e", "accountId": "a", "type": "INVALID", "amount": 1, "currency": "USD", "eventTimestamp": "2026-05-15T14:02:11Z"}, "type"),
    ({"eventId": "e", "accountId": "a", "type": "CREDIT", "amount": 0, "currency": "USD", "eventTimestamp": "2026-05-15T14:02:11Z"}, "amount"),
])
def test_validation_errors(client, payload, field):
    response = client.post("/events", json=payload)
    assert response.status_code == 422
