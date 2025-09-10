#!/usr/bin/env python3
import os
import shutil

# Service definitions with their specific functionality
services = {
    "mcp_EHRConnector": {
        "description": "EHR Data Connector MCP Service",
        "endpoints": [
            ("connect_ehr", "POST", "Establish connection to EHR system"),
            ("query_patients", "POST", "Query patient records from EHR"),
            ("extract_clinical_data", "POST", "Extract specific clinical data elements")
        ]
    },
    "mcp_ClaimsDataParser": {
        "description": "Claims Data Parser MCP Service", 
        "endpoints": [
            ("parse_claims", "POST", "Parse and structure claims data"),
            ("analyze_costs", "POST", "Analyze healthcare costs from claims"),
            ("identify_procedures", "POST", "Identify procedures and diagnoses from claims")
        ]
    },
    "mcp_SiteFeasibilityPredictor": {
        "description": "Site Feasibility Predictor MCP Service",
        "endpoints": [
            ("predict_feasibility", "POST", "Predict site feasibility score"),
            ("assess_capabilities", "POST", "Assess site capabilities and resources"),
            ("estimate_enrollment", "POST", "Estimate potential enrollment rates")
        ]
    },
    "mcp_DiversityIndexMapper": {
        "description": "Diversity Index Mapper MCP Service",
        "endpoints": [
            ("calculate_diversity", "POST", "Calculate diversity indices for sites"),
            ("map_demographics", "POST", "Map demographic distribution"),
            ("assess_representation", "POST", "Assess population representation")
        ]
    },
    "mcp_SoA_Comparator": {
        "description": "Schedule of Assessments Comparator MCP Service",
        "endpoints": [
            ("compare_schedules", "POST", "Compare study schedules"),
            ("analyze_burden", "POST", "Analyze patient and site burden"),
            ("optimize_visits", "POST", "Suggest visit schedule optimizations")
        ]
    }
}

# Base requirements content
requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
httpx==0.25.1
pydantic==2.5.0
pytest==7.4.3
pytest-asyncio==0.21.1
python-multipart==0.0.6
requests==2.31.0
pandas==2.1.3"""

# Base Dockerfile content
dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]"""

def generate_main_py(service_name, description, endpoints):
    """Generate main.py content for a service"""
    
    endpoint_code = ""
    for endpoint_name, method, doc in endpoints:
        endpoint_code += f'''
@app.post("/{endpoint_name}")
async def {endpoint_name}(data: Dict):
    """"{doc}"""
    try:
        # Mock implementation
        # In production, this would call actual dcri-mcp-tools
        result = {{
            "status": "success",
            "service": "{service_name}",
            "endpoint": "{endpoint_name}",
            "timestamp": datetime.now().isoformat(),
            "data": {{
                "mock_result": f"Processed by {endpoint_name}",
                "confidence": round(random.uniform(0.7, 0.95), 2)
            }}
        }}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    return f'''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import random

app = FastAPI(title="{description}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "service": "{service_name}"}}
{endpoint_code}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

# Create services
for service_name, config in services.items():
    service_path = f"services/{service_name}"
    
    # Create requirements.txt
    with open(f"{service_path}/requirements.txt", "w") as f:
        f.write(requirements_content)
    
    # Create Dockerfile
    with open(f"{service_path}/Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    # Create main.py
    main_content = generate_main_py(
        service_name, 
        config["description"], 
        config["endpoints"]
    )
    with open(f"{service_path}/main.py", "w") as f:
        f.write(main_content)
    
    print(f"Created service: {service_name}")

print("All services created successfully!")