import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "mcp_ProtocolComplexityScorer"

def test_score_protocol_valid():
    mock_protocol = {
        "protocol_text": "This is a Phase III, randomized, double-blind study involving 500 patients across 50 sites.",
        "analysis_depth": "standard"
    }
    
    response = client.post("/score", json=mock_protocol)
    assert response.status_code == 200
    
    data = response.json()
    assert "overall_score" in data
    assert "complexity_factors" in data
    assert "warnings" in data
    assert "recommendations" in data
    assert isinstance(data["overall_score"], float)
    assert 0 <= data["overall_score"] <= 10

def test_score_protocol_empty():
    response = client.post("/score", json={"protocol_text": ""})
    assert response.status_code == 200
    assert response.json()["overall_score"] < 1.0

def test_analyze_sections():
    response = client.post("/analyze_sections", json={"protocol_sections": {}})
    assert response.status_code == 200
    
    data = response.json()
    assert "section_analysis" in data
    assert "high_complexity_areas" in data
    assert "optimization_opportunities" in data

def test_score_protocol_complex():
    complex_protocol = {
        "protocol_text": "a" * 50000  # Very long protocol
    }
    
    response = client.post("/score", json=complex_protocol)
    assert response.status_code == 200
    
    data = response.json()
    assert data["overall_score"] > 5  # Should be complex
    assert len(data["warnings"]) > 0  # Should have warnings

if __name__ == "__main__":
    pytest.main([__file__])