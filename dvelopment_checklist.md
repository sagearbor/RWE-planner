# Local-First Development Plan: Global RWE Study Planner

This plan outlines a development workflow prioritizing local, containerized development and modular testing. The entire application stack (7 mock MCP services, 1 orchestrator, 1 frontend) will run on a local machine using Docker Compose, enabling parallel development and ensuring high fidelity with the future production environment on Azure.

### Phase 1: Local Environment Setup & Containerization (Sprint 1)

**Objective:** Create a fully containerized local development environment where all services can communicate. This is the foundation for the entire project.

- [ ] **Project Scaffolding**
  
  - [ ] Initialize Git repository: `rwe_study_planner_demo`.
    
  - [ ] Create the primary directory structure:
    
    ```
    rwe_study_planner_demo/├── services/│   ├── mcp_RealWorldDataIngestor/│   ├── mcp_EHRConnector/│   ├── mcp_ClaimsDataParser/│   ├── mcp_SiteFeasibilityPredictor/│   ├── mcp_DiversityIndexMapper/│   ├── mcp_ProtocolComplexityScorer/│   ├── mcp_SoA_Comparator/│   └── orchestrator/├── frontend/├── docker-compose.yml└── README.md
    ```
    
- [ ] **Base Container Definition**
  
  - [ ] In `services/mcp_RealWorldDataIngestor/`, create a `requirements.txt` file:
    
    ```
    fastapiuvicorn[standard]pytesthttpx
    ```
    
  - [ ] In the same directory, create a generic `Dockerfile` that will be copied to each service directory:
    
    ```
    FROM python:3.9-slimWORKDIR /appCOPY requirements.txt .RUN pip install --no-cache-dir -r requirements.txtCOPY . .CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```
    
- [ ] **Docker Compose Orchestration**
  
  - [ ] Create the `docker-compose.yml` file in the root directory. This file will define and network all our services.
    
    ```
    version: '3.8'services:  # --- Mock MCP Services ---  mcp_datainjestor:    build: ./services/mcp_RealWorldDataIngestor    container_name: mcp_datainjestor_svc    volumes:      - ./services/mcp_RealWorldDataIngestor:/app  # ... (Define similar services for EHRConnector, ClaimsDataParser, etc.) ...  # --- Core Backend Service ---  orchestrator:    build: ./services/orchestrator    container_name: orchestrator_svc    ports:      - "8080:8000" # Expose orchestrator on host port 8080    volumes:      - ./services/orchestrator:/app    depends_on:      - mcp_datainjestor # Add all 7 MCP services here  # --- Frontend Service ---  frontend:    build: ./frontend    container_name: frontend_ui    ports:      - "3000:3000"    volumes:      - ./frontend:/app    depends_on:      - orchestrator
    ```
    

### Phase 2: Modular MCP Service Development & Unit Testing (Sprint 2-3)

**Objective:** Build and test each of the 7 mock MCP services independently. This work can be parallelized. The process below should be repeated for **each** of the 7 MCPs.

- [ ] **For service `mcp_ProtocolComplexityScorer` (Example):**
  
  - [ ] Copy the generic `Dockerfile` and `requirements.txt` into `services/mcp_ProtocolComplexityScorer/`.
    
  - [ ] Create `main.py` with a simple FastAPI endpoint.
    
    ```
    # services/mcp_ProtocolComplexityScorer/main.pyfrom fastapi import FastAPI, HTTPExceptionfrom pydantic import BaseModelclass ProtocolInput(BaseModel):    protocol_text: strapp = FastAPI()@app.post("/score")def get_complexity_score(data: ProtocolInput):    # Mock logic: score is based on text length    score = len(data.protocol_text) / 1000    return {"complexity_score": round(score, 2), "warnings": ["Section 5.2 is verbose"]}
    ```
    
  - [ ] Create `test_main.py` to unit test the endpoint logic.
    
    ```
    # services/mcp_ProtocolComplexityScorer/test_main.pyfrom fastapi.testclient import TestClientfrom .main import appclient = TestClient(app)def test_complexity_scorer_valid():    # Mock input data    mock_protocol = "a" * 5000     response = client.post("/score", json={"protocol_text": mock_protocol})    assert response.status_code == 200    data = response.json()    assert data["complexity_score"] == 5.0    assert "warnings" in datadef test_complexity_scorer_empty():    response = client.post("/score", json={"protocol_text": ""})    assert response.status_code == 200    assert response.json()["complexity_score"] == 0.0
    ```
    
  - [ ] Run tests from within the service directory to confirm functionality: `pytest`.
    
- [ ] **Repeat the above process for all 7 MCP services.**
  

### Phase 3: Backend Orchestrator Development & Integration Testing (Sprint 4)

**Objective:** Build the orchestrator service that correctly calls the sequence of MCP services within the Docker network.

- [ ] **Orchestrator Logic**
  
  - [ ] In `services/orchestrator/main.py`, create the main endpoint.
    
  - [ ] Use a library like `httpx` to make calls to the other services. **Crucially, use the service names from `docker-compose.yml` as hostnames.** Docker's internal DNS will resolve them.
    
    ```
    # services/orchestrator/main.pyimport httpx# ... FastAPI setup ...@app.post("/plan-rwe-study")async def plan_study(data: RWEPlannerInput):    async with httpx.AsyncClient() as client:        # Call MCPs in logical order        score_response = await client.post(            "http://mcp_protocolscorer_svc:8000/score", # Note the service name            json={"protocol_text": data.protocol_text}        )        score_data = score_response.json()        # ... continue chain of calls, transforming data as needed ...    # ... run final synthesis algorithm ...    return {"final_plan": ...}
    ```
    
- [ ] **Integration Testing**
  
  - [ ] In `services/orchestrator/test_main.py`, test the orchestrator's logic.
    
  - [ ] Use `pytest-mock` to **mock the `httpx` calls**. This isolates the orchestrator's own logic (data transformation, synthesis algorithm) without needing the other services to be perfect.
    
    ```
    # services/orchestrator/test_main.pydef test_orchestrator_flow(mocker):    # Mock the response from the complexity scorer service    mock_post = mocker.patch("httpx.AsyncClient.post")    mock_post.return_value = httpx.Response(200, json={"complexity_score": 3.5})    # Call the orchestrator's endpoint    response = client.post("/plan-rwe-study", json={...})    # Assert that the orchestrator processed the mocked data correctly    assert response.status_code == 200    # ... more assertions on the final synthesis logic ...
    ```
    
  - [ ] Run `docker-compose up -d` to start all services, then manually test the orchestrator endpoint (e.g., with Postman or curl) at `http://localhost:8080/plan-rwe-study` for a true end-to-end test of the local stack.
    

### Phase 4 & 5: Frontend Development and "Stitching to Azure"

These phases remain conceptually similar but are now built on the containerized foundation.

- [ ] **Frontend Development (Local)**
  
  - [ ] The frontend team can work entirely locally. Their `fetch` or `axios` calls will be configured to point to the orchestrator's local URL: `http://localhost:8080/api/v1`.
    
  - [ ] The entire application can be demoed and tested by simply running `docker-compose up`.
    
- [ ] **"Stitching to Azure" - Deployment Plan**
  
  - [ ] **1. Azure Container Registry (ACR):** Create a private ACR instance to store your Docker images.
    
  - [ ] **2. CI/CD Pipeline (GitHub Actions):** Create a `.github/workflows/deploy.yml` file.
    
    - [ ] Add a step to log in to Azure (`azure/login`).
      
    - [ ] Add a step to log in to ACR (`docker login ...`).
      
    - [ ] For **each service** (all 8), add a step to:
      
      - `docker build -t <your_acr>/<service_name>:<tag> .`
        
      - `docker push <your_acr>/<service_name>:<tag>`
        
  - [ ] **3. Azure App Service:**
    
    - [ ] Provision 8 separate "App Service for Containers" instances (one for each service).
      
    - [ ] Configure each App Service to pull its specific image from your ACR.
      
    - [ ] Use "App Service Configuration" to set environment variables. The URLs for the MCP services will now be their Azure hostnames (e.g., `https://mcp-protocolscorer.azurewebsites.net`). The orchestrator's code must be updated to use these URLs in a production environment.
      
  - [ ] **4. Networking & CORS:** Configure Cross-Origin Resource Sharing (CORS) on all the backend App Services to allow requests from the frontend's domain.
