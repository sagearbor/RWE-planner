#!/usr/bin/env python3
import os

# Update all Dockerfiles to use port 8240
services = [
    "mcp_RealWorldDataIngestor",
    "mcp_EHRConnector", 
    "mcp_ClaimsDataParser",
    "mcp_SiteFeasibilityPredictor",
    "mcp_DiversityIndexMapper",
    "mcp_ProtocolComplexityScorer",
    "mcp_SoA_Comparator",
    "orchestrator"
]

dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8240", "--reload"]"""

for service in services:
    dockerfile_path = f"services/{service}/Dockerfile"
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)
    print(f"Updated {dockerfile_path}")

# Also update main.py files to use port 8240
for service in services:
    main_path = f"services/{service}/main.py"
    if os.path.exists(main_path):
        with open(main_path, "r") as f:
            content = f.read()
        
        # Replace port 8000 with 8240 in the main.py files
        content = content.replace('port=8000', 'port=8240')
        
        with open(main_path, "w") as f:
            f.write(content)
        print(f"Updated {main_path}")

print("All services updated to use port 8240")