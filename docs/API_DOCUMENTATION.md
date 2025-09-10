# RWE Study Planner API Documentation

## Overview
The RWE Study Planner provides a RESTful API for planning Real-World Evidence studies. The API orchestrates multiple MCP services to analyze protocols, identify data sources, and recommend optimal study sites.

## Base URLs
- **Local Development**: `http://localhost:8250`
- **Production (Azure)**: `https://rwe-orchestrator.azurewebsites.net`

## Authentication
Currently, the API does not require authentication for development. Production deployment will use Azure AD authentication.

## Main Endpoints

### 1. Plan RWE Study
**Endpoint**: `POST /plan_rwe_study`

Performs comprehensive RWE study planning by orchestrating all MCP services.

**Request Body**:
```json
{
  "protocol_text": "string",
  "disease_area": "string",
  "target_countries": ["string"],
  "target_enrollment": "integer",
  "inclusion_criteria": ["string"],
  "exclusion_criteria": ["string"],
  "study_duration_months": "integer",
  "primary_endpoints": ["string"],
  "secondary_endpoints": ["string"]
}
```

**Response** (200 OK):
```json
{
  "study_id": "RWE_20240101_120000",
  "protocol_complexity_score": 5.5,
  "estimated_total_cohort_size": 5000,
  "recommended_sites": [
    {
      "site_id": "USA_SITE_001",
      "site_name": "USA Clinical Research Site 1",
      "country": "USA",
      "feasibility_score": 8.5,
      "diversity_score": 7.8,
      "data_availability_score": 8.0,
      "overall_rank": 1,
      "strengths": ["Strong enrollment history"],
      "challenges": ["Limited parking"]
    }
  ],
  "data_sources": [
    {
      "source_id": "USA_EHR_123",
      "source_name": "USA National EHR Database",
      "data_type": "EHR",
      "geography": "USA",
      "patient_count": 45000,
      "quality_score": 8.9,
      "availability": "Available"
    }
  ],
  "timeline_estimate": {
    "startup_months": 3,
    "enrollment_months": 12,
    "total_months": 18
  },
  "risk_factors": ["Protocol document is very lengthy"],
  "optimization_opportunities": ["Consider simplifying protocol procedures"]
}
```

### 2. Quick Assessment
**Endpoint**: `POST /quick_assessment`

Performs a quick protocol complexity assessment without full analysis.

**Request Body**:
```json
{
  "protocol_text": "string"
}
```

**Response** (200 OK):
```json
{
  "assessment": "quick",
  "complexity": {
    "overall_score": 5.5,
    "complexity_factors": {},
    "warnings": [],
    "recommendations": []
  },
  "recommendation": "Proceed with full planning"
}
```

### 3. Health Check
**Endpoint**: `GET /health`

Returns the health status of the orchestrator service.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "orchestrator",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 4. Service Status
**Endpoint**: `GET /service_status`

Returns the status of all MCP services.

**Response** (200 OK):
```json
{
  "data_ingestor": "healthy",
  "ehr_connector": "healthy",
  "claims_parser": "healthy",
  "feasibility_predictor": "healthy",
  "diversity_mapper": "healthy",
  "protocol_scorer": "healthy",
  "soa_comparator": "healthy"
}
```

## MCP Service Endpoints

Each MCP service exposes its own endpoints on ports 8241-8247 (local) or as Azure Web Apps (production).

### Protocol Complexity Scorer (Port 8246)
- `POST /score` - Score protocol complexity
- `POST /analyze_sections` - Analyze specific protocol sections

### Real World Data Ingestor (Port 8241)
- `POST /identify_sources` - Identify available data sources
- `POST /estimate_cohort_size` - Estimate potential cohort size
- `POST /data_quality_assessment` - Assess data quality

### EHR Connector (Port 8242)
- `POST /connect_ehr` - Establish EHR connection
- `POST /query_patients` - Query patient records
- `POST /extract_clinical_data` - Extract clinical data

### Claims Data Parser (Port 8243)
- `POST /parse_claims` - Parse claims data
- `POST /analyze_costs` - Analyze healthcare costs
- `POST /identify_procedures` - Identify procedures from claims

### Site Feasibility Predictor (Port 8244)
- `POST /predict_feasibility` - Predict site feasibility
- `POST /assess_capabilities` - Assess site capabilities
- `POST /estimate_enrollment` - Estimate enrollment rates

### Diversity Index Mapper (Port 8245)
- `POST /calculate_diversity` - Calculate diversity indices
- `POST /map_demographics` - Map demographic distribution
- `POST /assess_representation` - Assess population representation

### SoA Comparator (Port 8247)
- `POST /compare_schedules` - Compare study schedules
- `POST /analyze_burden` - Analyze patient/site burden
- `POST /optimize_visits` - Suggest visit optimizations

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Missing required fields: protocol_text",
  "status_code": 400,
  "path": "/plan_rwe_study"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "target_enrollment"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "status_code": 500,
  "path": "/plan_rwe_study"
}
```

### 503 Service Unavailable
```json
{
  "error": "Service mcp_protocolscorer is unavailable",
  "status_code": 503,
  "path": "/plan_rwe_study"
}
```

## Rate Limiting
- Development: No rate limiting
- Production: 100 requests per minute per IP

## CORS
CORS is enabled for all origins in development. Production will restrict to specific domains.

## Monitoring
All API calls are logged with structured logging including:
- Request/response times
- Status codes
- Error details
- Service dependencies

## WebSocket Support
Future versions will support WebSocket connections for real-time study planning updates.