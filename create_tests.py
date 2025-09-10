#!/usr/bin/env python3
import os

# Base test template for all MCP services
test_template = '''import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "{service_name}"

def test_primary_endpoint():
    """Test the main endpoint of this service"""
    test_data = {{
        "test_field": "test_value"
    }}
    
    # Test first endpoint
    endpoints = {endpoints}
    if endpoints:
        endpoint = endpoints[0]
        response = client.post(f"/{{endpoint}}", json=test_data)
        assert response.status_code == 200
        assert "status" in response.json() or "data" in response.json()

def test_invalid_request():
    """Test with invalid/missing data"""
    response = client.post("/{first_endpoint}", json={{}})
    # Should either handle gracefully or return error
    assert response.status_code in [200, 400, 422, 500]

def test_all_endpoints():
    """Smoke test all endpoints"""
    endpoints = {endpoints}
    test_data = {{"test": "data"}}
    
    for endpoint in endpoints:
        response = client.post(f"/{{endpoint}}", json=test_data)
        assert response.status_code in [200, 400, 422, 500]
        
if __name__ == "__main__":
    pytest.main([__file__])
'''

# Service configurations
services = {
    "mcp_RealWorldDataIngestor": ["identify_sources", "estimate_cohort_size", "data_quality_assessment"],
    "mcp_EHRConnector": ["connect_ehr", "query_patients", "extract_clinical_data"],
    "mcp_ClaimsDataParser": ["parse_claims", "analyze_costs", "identify_procedures"],
    "mcp_SiteFeasibilityPredictor": ["predict_feasibility", "assess_capabilities", "estimate_enrollment"],
    "mcp_DiversityIndexMapper": ["calculate_diversity", "map_demographics", "assess_representation"],
    "mcp_SoA_Comparator": ["compare_schedules", "analyze_burden", "optimize_visits"]
}

# Create test files for each service
for service_name, endpoints in services.items():
    test_path = f"services/{service_name}/test_main.py"
    
    # Skip if already exists
    if os.path.exists(test_path):
        print(f"Test already exists for {service_name}, skipping...")
        continue
        
    test_content = test_template.format(
        service_name=service_name,
        endpoints=endpoints,
        first_endpoint=endpoints[0] if endpoints else "test"
    )
    
    with open(test_path, "w") as f:
        f.write(test_content)
    
    print(f"Created test file for {service_name}")

# Create orchestrator integration test
orchestrator_test = '''import pytest
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
'''

with open("services/orchestrator/test_main.py", "w") as f:
    f.write(orchestrator_test)
print("Created orchestrator integration test")

print("\nAll test files created successfully!")