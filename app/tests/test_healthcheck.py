def test_healthcheck(client):
    """Test that the healthcheck endpoint is working"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}