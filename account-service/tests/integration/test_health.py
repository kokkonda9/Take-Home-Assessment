def test_health_returns_up(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "UP"
    assert body["service"] == "account-service"
    assert body["database"] == "UP"
