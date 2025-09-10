# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Global RWE Study Planner is a containerized microservices application that wraps and orchestrates tools from the dcri-mcp-tools repository (https://github.com/sagearbor/dcri-mcp-tools) to provide comprehensive Real-World Evidence study design and site selection. The system uses Docker Compose for local development and is designed for deployment to Azure App Services.

## Architecture

### Service Components
- **7 MCP Service Wrappers** (FastAPI-based microservices that call dcri-mcp-tools):
  - `mcp_RealWorldDataIngestor` - Wraps data ingestion tools for EHR/Claims data
  - `mcp_EHRConnector` - Interfaces with EHR data extraction tools
  - `mcp_ClaimsDataParser` - Processes claims data using parsing tools
  - `mcp_SiteFeasibilityPredictor` - Analyzes site feasibility metrics
  - `mcp_DiversityIndexMapper` - Calculates and maps diversity indices
  - `mcp_ProtocolComplexityScorer` - Uses clinical_protocol_qa.py and related tools
  - `mcp_SoA_Comparator` - Compares schedules of assessments
- **Orchestrator Service**: Coordinates calls to all MCP services and synthesizes results
- **Frontend**: React-based UI served on port 3000

### Directory Structure (once scaffolded)
```
rwe_study_planner_demo/
├── services/
│   ├── mcp_[ServiceName]/
│   │   ├── main.py         # FastAPI application
│   │   ├── test_main.py    # Unit tests
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── orchestrator/
├── frontend/
├── docker-compose.yml
└── README.md
```

## Development Commands

### Initial Setup
```bash
# Clone and navigate to repository
git clone [repository_url]
cd rwe_study_planner_demo

# Build and run all services
docker-compose up --build -d

# View logs for all services
docker-compose logs -f

# Stop all services
docker-compose down
```

### Service Development
```bash
# Run tests for a specific service
cd services/mcp_[ServiceName]
pytest

# Test individual service endpoint (while containers are running)
curl -X POST http://localhost:8080/[endpoint] -H "Content-Type: application/json" -d '{...}'

# Rebuild specific service
docker-compose build [service_name]
docker-compose up -d [service_name]
```

### Testing
```bash
# Run unit tests for a service
cd services/[service_name]
pytest

# Run integration tests (requires all services running)
docker-compose up -d
pytest services/orchestrator/test_main.py
```

## Key Development Patterns

### Service Communication
- Services communicate via HTTP within Docker's internal network
- Use service names from docker-compose.yml as hostnames (e.g., `http://mcp_protocolscorer_svc:8000`)
- Orchestrator uses httpx AsyncClient for non-blocking calls to MCP services

### Testing Strategy
- Each MCP service has isolated unit tests using FastAPI's TestClient
- Orchestrator tests use pytest-mock to mock httpx calls to MCP services
- End-to-end testing via docker-compose environment

### API Endpoints
- MCP services expose specific endpoints (e.g., `/score`, `/analyze`, `/predict`)
- Orchestrator exposes `/plan-rwe-study` endpoint on port 8080
- Frontend accesses orchestrator at `http://localhost:8080/api/v1`

## Azure Deployment Considerations
- Each service will be deployed as a separate Azure App Service for Containers
- Service URLs will change from Docker service names to Azure hostnames
- Environment variables will be used to configure service endpoints in production
- CORS configuration required for frontend-backend communication