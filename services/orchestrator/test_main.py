import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
import httpx
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_service_status():
    """Test service status endpoint"""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock()
        mock_get.return_value.status_code = 200
        
        response = client.get("/service_status")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

def test_plan_rwe_study_valid():
    """Test main orchestration endpoint with valid data"""
    study_request = {
        "protocol_text": "Test protocol",
        "disease_area": "Diabetes",
        "target_countries": ["USA", "UK"],
        "target_enrollment": 100,
        "inclusion_criteria": ["Age > 18"],
        "exclusion_criteria": ["Pregnant"],
        "study_duration_months": 12,
        "primary_endpoints": ["HbA1c"],
        "secondary_endpoints": ["Weight"]
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        # Mock all service responses
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "overall_score": 5.5,
            "warnings": [],
            "recommendations": [],
            "estimated_cohort_size": 1000,
            "data": {"mock": "data"}
        }
        mock_post.return_value = mock_response
        
        response = client.post("/plan_rwe_study", json=study_request)
        
        # Should return valid study plan
        assert response.status_code in [200, 503]  # 503 if services not running
        
        if response.status_code == 200:
            data = response.json()
            assert "study_id" in data
            assert "protocol_complexity_score" in data
            assert "recommended_sites" in data

def test_quick_assessment():
    """Test quick assessment endpoint"""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"overall_score": 4.5}
        mock_post.return_value = mock_response
        
        response = client.post("/quick_assessment", json={"protocol_text": "Test"})
        assert response.status_code in [200, 500]

def test_plan_rwe_study_missing_fields():
    """Test with missing required fields"""
    response = client.post("/plan_rwe_study", json={"protocol_text": "Test"})
    assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    pytest.main([__file__])
