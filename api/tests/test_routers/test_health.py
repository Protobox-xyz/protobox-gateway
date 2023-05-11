def test_health_api(api):
    response = api.get("/api/health/")
    assert response.is_success
