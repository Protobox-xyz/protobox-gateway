def test_health_api(api):
    response = api.get("http://0.0.0.0:8000/api/health/")
    assert response.is_success
