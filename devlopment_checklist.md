# Local-First Development Plan: Global RWE Study Planner

This plan outlines a development workflow prioritizing local, containerized development and modular testing. The entire application stack (7 mock MCP services, 1 orchestrator, 1 frontend) will run on a local machine using Docker Compose, enabling parallel development and ensuring high fidelity with the future production environment on Azure.

### Phase 1: Local Environment Setup & Containerization (Sprint 1) ✅

**Objective:** Create a fully containerized local development environment where all services can communicate. This is the foundation for the entire project.

- [x] **Project Scaffolding**
  
  - [x] Initialize Git repository: `RWE-planner`.
    
  - [x] Create the primary directory structure:
    
    ```
    RWE-planner/
    ├── services/
    │   ├── mcp_RealWorldDataIngestor/
    │   ├── mcp_EHRConnector/
    │   ├── mcp_ClaimsDataParser/
    │   ├── mcp_SiteFeasibilityPredictor/
    │   ├── mcp_DiversityIndexMapper/
    │   ├── mcp_ProtocolComplexityScorer/
    │   ├── mcp_SoA_Comparator/
    │   └── orchestrator/
    ├── frontend/
    ├── docker-compose.yml
    └── README.md
    ```
    
- [x] **Base Container Definition**
  
  - [x] Created `requirements.txt` files for all services with FastAPI, uvicorn, pytest, httpx
    
  - [x] Created Dockerfiles for all services (using port 8240 instead of 8000)
    
- [x] **Docker Compose Orchestration**
  
  - [x] Created `docker-compose.yml` file with all services networked together
    
    ```
    version: '3.8'services:  # --- Mock MCP Services ---  mcp_datainjestor:    build: ./services/mcp_RealWorldDataIngestor    container_name: mcp_datainjestor_svc    volumes:      - ./services/mcp_RealWorldDataIngestor:/app  # ... (Define similar services for EHRConnector, ClaimsDataParser, etc.) ...  # --- Core Backend Service ---  orchestrator:    build: ./services/orchestrator    container_name: orchestrator_svc    ports:      - "8080:8000" # Expose orchestrator on host port 8080    volumes:      - ./services/orchestrator:/app    depends_on:      - mcp_datainjestor # Add all 7 MCP services here  # --- Frontend Service ---  frontend:    build: ./frontend    container_name: frontend_ui    ports:      - "3000:3000"    volumes:      - ./frontend:/app    depends_on:      - orchestrator
    ```
    

### Phase 2: Modular MCP Service Development & Unit Testing (Sprint 2-3) ✅

**Objective:** Build and test each of the 7 mock MCP services independently. This work can be parallelized. The process below should be repeated for **each** of the 7 MCPs.

- [x] **All MCP Services Implemented:**
  
  - [x] `mcp_ProtocolComplexityScorer` - Analyzes protocol complexity with scoring endpoints
  - [x] `mcp_RealWorldDataIngestor` - Identifies data sources and estimates cohort sizes
  - [x] `mcp_EHRConnector` - Mock EHR connection and data extraction
  - [x] `mcp_ClaimsDataParser` - Parses and analyzes claims data
  - [x] `mcp_SiteFeasibilityPredictor` - Predicts site performance and capabilities
  - [x] `mcp_DiversityIndexMapper` - Calculates diversity indices and demographics
  - [x] `mcp_SoA_Comparator` - Compares schedules and analyzes burden
    
- [x] **For each service:**
  
  - [x] Created `requirements.txt` with FastAPI, uvicorn, httpx, pytest dependencies
  - [x] Created `Dockerfile` configured for port 8240
  - [x] Created `main.py` with FastAPI endpoints and mock logic
  - [x] Created `test_main.py` with comprehensive unit tests
  - [x] All services include health check endpoints at `/health`
  

### Phase 3: Backend Orchestrator Development & Integration Testing (Sprint 4) ✅

**Objective:** Build the orchestrator service that correctly calls the sequence of MCP services within the Docker network.

- [x] **Orchestrator Logic**
  
  - [x] Created `services/orchestrator/main.py` with comprehensive orchestration logic
  - [x] Implemented `/plan_rwe_study` endpoint that coordinates all MCP services
  - [x] Added `/quick_assessment` for rapid protocol evaluation
  - [x] Implemented `/service_status` to check health of all MCP services
  - [x] Used httpx AsyncClient for non-blocking parallel service calls
  - [x] Service URLs configured with Docker service names (port 8240)
    
- [x] **Integration Testing**
  
  - [x] Created `services/orchestrator/test_main.py` with mocked httpx calls
  - [x] Tests cover main orchestration flow, error handling, and validation
  - [x] All services accessible via Docker Compose at ports 8241-8250
    

### Phase 4 & 5: Frontend Development and "Stitching to Azure" ✅

These phases remain conceptually similar but are now built on the containerized foundation.

- [x] **Frontend Development (Local)**
  
  - [x] Created React 18 frontend with comprehensive UI components
  - [x] Implemented interactive dashboard with real-time service status
  - [x] Added data visualization with Chart.js (complexity scores, site rankings)
  - [x] Created StudyResults component for displaying orchestrated results
  - [x] Added ServiceStatus component for monitoring MCP health
  - [x] Configured axios to call orchestrator at `http://localhost:8250`
  - [x] Application runs via `docker-compose up` on port 3000
    
- [x] **"Stitching to Azure" - Deployment Plan**
  
  - [x] **1. Azure Container Registry (ACR):** 
    - [x] Created deployment scripts for ACR setup (`azure/deploy.sh`)
    
  - [x] **2. CI/CD Pipeline (GitHub Actions):** 
    - [x] Created `.github/workflows/ci-cd.yml` with complete pipeline
    - [x] Tests run for all services in parallel
    - [x] Docker images built and pushed to GitHub Container Registry
    - [x] Deployment to Azure App Service on main branch merge
      
  - [x] **3. Azure Infrastructure:**
    - [x] Created ARM template (`azure/azuredeploy.json`)
    - [x] Configured for 9 App Services (7 MCP + orchestrator + frontend)
    - [x] Environment variables configured for production URLs
    - [x] Key Vault integration for secrets management
      
  - [x] **4. Networking & CORS:** 
    - [x] CORS configured in all FastAPI services
    - [x] Frontend configured with production API URL

### Additional Enhancements Completed ✅

- [x] **Error Handling & Logging**
  - [x] Created structured logging utility (`services/utils/logger.py`)
  - [x] Implemented centralized error handler (`services/utils/error_handler.py`)
  - [x] Added health check utilities for service monitoring
  
- [x] **Documentation**
  - [x] Created comprehensive API documentation (`docs/API_DOCUMENTATION.md`)
  - [x] Created architecture documentation (`docs/ARCHITECTURE.md`)
  - [x] Created local running instructions (`RUNNING_LOCALLY.md`)
  - [x] Updated CLAUDE.md with project-specific guidance
  
- [x] **Testing**
  - [x] Unit tests for all 7 MCP services
  - [x] Integration tests for orchestrator
  - [x] Mocked external dependencies with pytest-mock
  
- [x] **Project Structure**
  - [x] Clean separation of concerns
  - [x] Modular service architecture
  - [x] Shared utilities for consistency
  - [x] Docker Compose for local development
  - [x] Azure deployment ready

## Summary

✅ **All phases completed successfully!**

The RWE Study Planner is now:
1. Fully containerized with Docker
2. Running locally on ports 8241-8250 (backend) and 3000 (frontend)
3. Tested with comprehensive unit and integration tests
4. Documented with API specs and architecture diagrams
5. Ready for Azure deployment with CI/CD pipeline
6. Configured to integrate with dcri-mcp-tools when ready

To run locally:
```bash
docker-compose up --build -d
```

Then access:
- Frontend: http://localhost:3000
- API: http://localhost:8250
- Individual services: http://localhost:8241-8247
