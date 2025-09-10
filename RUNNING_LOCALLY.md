# Running the RWE Study Planner Locally

## Prerequisites
- Docker and Docker Compose installed
- At least 4GB of free RAM
- Ports 8241-8250 and 3000 available

## Quick Start

1. **Build and start all services:**
```bash
docker-compose up --build -d
```

This will:
- Build all 7 MCP service containers
- Build the orchestrator service container
- Build the frontend React application
- Start all services in the background

2. **Access the application:**
- Frontend UI: http://localhost:3000
- Orchestrator API: http://localhost:8250
- Individual MCP services: http://localhost:8241-8247

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React UI |
| Orchestrator | 8250 | Main API endpoint |
| Data Ingestor | 8241 | RWE data source identification |
| EHR Connector | 8242 | EHR data extraction |
| Claims Parser | 8243 | Claims data processing |
| Site Feasibility | 8244 | Site feasibility prediction |
| Diversity Mapper | 8245 | Diversity index calculation |
| Protocol Scorer | 8246 | Protocol complexity scoring |
| SoA Comparator | 8247 | Schedule of assessments comparison |

## Monitoring Services

### View logs for all services:
```bash
docker-compose logs -f
```

### View logs for specific service:
```bash
docker-compose logs -f orchestrator
docker-compose logs -f frontend
```

### Check service health:
```bash
curl http://localhost:8250/health
curl http://localhost:8250/service_status
```

## Testing the Application

1. Open http://localhost:3000 in your browser
2. Click "Load Sample Data" to populate the form with example data
3. Click "Plan RWE Study" to see the analysis results
4. The service status panel shows the health of all MCP services

## Stopping Services

### Stop all services:
```bash
docker-compose down
```

### Stop and remove all containers and volumes:
```bash
docker-compose down -v
```

## Troubleshooting

### Port conflicts:
If you get port binding errors, check if the ports are in use:
```bash
lsof -i :3000
lsof -i :8250
```

### Service connectivity issues:
Check that all services are running:
```bash
docker-compose ps
```

### Rebuild specific service:
```bash
docker-compose build mcp_protocolscorer
docker-compose up -d mcp_protocolscorer
```

### View container resource usage:
```bash
docker stats
```

## Development Mode

For development with hot-reload:

1. **Backend services:**
The services already run with `--reload` flag in development mode.

2. **Frontend development:**
```bash
cd frontend
npm install
npm start
```

3. **Test individual MCP service:**
```bash
curl -X POST http://localhost:8246/score \
  -H "Content-Type: application/json" \
  -d '{"protocol_text": "Sample protocol text"}'
```

## API Documentation

### Main Orchestrator Endpoint:
POST http://localhost:8250/plan_rwe_study

Request body example:
```json
{
  "protocol_text": "Protocol description...",
  "disease_area": "Type 2 Diabetes",
  "target_countries": ["USA", "UK"],
  "target_enrollment": 500,
  "inclusion_criteria": ["Age 18-75"],
  "exclusion_criteria": ["Type 1 diabetes"],
  "study_duration_months": 12,
  "primary_endpoints": ["HbA1c change"],
  "secondary_endpoints": ["Weight change"]
}
```

## Next Steps

- The mock MCP services currently return simulated data
- In production, these will call the actual dcri-mcp-tools API endpoints
- Azure deployment configuration is ready in the docker-compose.yml file