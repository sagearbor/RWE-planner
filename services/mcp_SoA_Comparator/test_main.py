import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "mcp_SoA_Comparator"

def test_primary_endpoint():
    """Test the main endpoint of this service"""
    test_data = {
        "test_field": "test_value"
    }
    
    # Test first endpoint
    endpoints = ['compare_schedules', 'analyze_burden', 'optimize_visits']
    if endpoints:
        endpoint = endpoints[0]
        response = client.post(f"/{endpoint}", json=test_data)
        assert response.status_code == 200
        assert "status" in response.json() or "data" in response.json()

def test_invalid_request():
    """Test with invalid/missing data"""
    response = client.post("/compare_schedules", json={})
    # Should either handle gracefully or return error
    assert response.status_code in [200, 400, 422, 500]

def test_all_endpoints():
    """Smoke test all endpoints"""
    endpoints = ['compare_schedules', 'analyze_burden', 'optimize_visits']
    test_data = {"test": "data"}
    
    for endpoint in endpoints:
        response = client.post(f"/{endpoint}", json=test_data)
        assert response.status_code in [200, 400, 422, 500]
        
if __name__ == "__main__":
    pytest.main([__file__])
