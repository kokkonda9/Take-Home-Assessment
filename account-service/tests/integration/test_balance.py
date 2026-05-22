def test_balance_not_found(client):
    response = client.get("/accounts/unknown/balance")
    assert response.status_code == 404
