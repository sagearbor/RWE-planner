# Global RWE Study Planner

**A synergistic tool that integrates seven MCP services to provide a comprehensive, data-driven approach to Real-World Evidence (RWE) study design and site selection.**
Overview available at https://g.co/gemini/share/42ac8f27887a 

### 1. Problem Statement

Planning RWE studies is a complex, multi-faceted process that relies on fragmented data and siloed expertise. Key questions about protocol complexity, data source availability, site feasibility, and patient diversity are often answered sequentially and with incomplete information. This leads to inefficient planning cycles, costly protocol amendments, and suboptimal site selection.

### 2. The Solution: An Integrated Planning Hub

The **Global RWE Study Planner** transforms this fragmented process into a unified, interactive experience. By orchestrating a suite of specialized MCP tools, it provides study planners with a single interface to:

- **Instantly assess protocol complexity** before significant resources are committed.
  
- **Identify viable real-world data sources** (EHR, Claims) globally.
  
- **Predict site feasibility** based on data-driven metrics.
  
- **Analyze potential for patient diversity** across candidate sites.
  
- **Compare operational overhead** against standard schedules of assessments.
  

This holistic view allows for rapid iteration on study designs and empowers teams to select the most promising sites with confidence.

### 3. Key Features

- **Interactive Dashboard:** A single-pane-of-glass view combining map-based data visualization with sortable results tables.
  
- **Protocol Scoring:** Real-time feedback on the complexity and potential challenges of a study protocol.
  
- **Automated Data Ingestion:** Connects to and parses various real-world data sources to estimate cohort size.
  
- **Multi-Factor Site Ranking:** Generates a synthesized score for each potential site based on feasibility, diversity, and data availability.
  

### 4. MCPs Integrated

This solution achieves its power by synergizing the following seven MCP tools:

1. `RealWorldDataIngestor`
  
2. `EHRConnector`
  
3. `ClaimsDataParser`
  
4. `SiteFeasibilityPredictor`
  
5. `DiversityIndexMapper`
  
6. `ProtocolComplexityScorer`
  
7. `SoA_Comparator`
  

### 5. Local Development & Setup

This project is designed for a local-first, containerized workflow using Docker.

1. **Clone the repository:**
  
  ```
  git clone [repository_url]cd rwe_study_planner_demo
  ```
  
2. **Build and run all services:** This single command will build the images for all 7 mock MCPs, the orchestrator, and the frontend, then start them in a networked environment.
  
  ```
  docker-compose up --build -d
  ```
  
3. **Access the application:**
  
  - **Frontend UI:** [http://localhost:3000](https://www.google.com/search?q=http://localhost:3000 "null")
    
  - **Orchestrator API:** [http://localhost:8080](https://www.google.com/search?q=http://localhost:8080 "null")
