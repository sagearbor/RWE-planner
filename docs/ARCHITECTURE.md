# RWE Study Planner Architecture

## System Overview

The RWE Study Planner is a microservices-based application designed to streamline Real-World Evidence study planning through intelligent orchestration of specialized services.

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                      │
│                          Port: 3000                          │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Service                       │
│                        Port: 8250                            │
│                 Coordinates all MCP services                 │
└──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────────┘
       │      │      │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼      ▼      ▼
   ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
   │ Data ││ EHR  ││Claims││ Site ││Diver-││Proto-││ SoA  │
   │Inges-││Conn- ││Parser││Feasi-││ sity ││ col  ││Compa-│
   │ tor   ││ector ││      ││bility││Mapper││Scorer││rator │
   │ 8241 ││ 8242 ││ 8243 ││ 8244 ││ 8245 ││ 8246 ││ 8247 │
   └──────┘└──────┘└──────┘└──────┘└──────┘└──────┘└──────┘
```

## Technology Stack

### Backend
- **Language**: Python 3.9
- **Framework**: FastAPI
- **Async HTTP**: httpx
- **Testing**: pytest, pytest-asyncio
- **Containerization**: Docker
- **Orchestration**: Docker Compose

### Frontend
- **Framework**: React 18
- **UI Library**: React Bootstrap
- **Charts**: Chart.js with react-chartjs-2
- **HTTP Client**: Axios
- **Build Tool**: Create React App

### Infrastructure
- **Container Registry**: Azure Container Registry
- **Hosting**: Azure App Service (Linux containers)
- **Secrets Management**: Azure Key Vault
- **CI/CD**: GitHub Actions
- **Monitoring**: Azure Application Insights (planned)

## Service Architecture

### 1. Orchestrator Service
**Responsibility**: Central coordination and workflow management
- Receives study planning requests from frontend
- Orchestrates calls to MCP services in optimal sequence
- Aggregates and synthesizes results
- Handles error recovery and fallback strategies

**Key Features**:
- Parallel service calls where possible
- Circuit breaker pattern for resilience
- Response caching for performance
- Comprehensive error handling

### 2. MCP Services
Each MCP service is a specialized microservice focusing on a specific aspect of RWE study planning:

#### Data Ingestor (8241)
- Identifies available RWE data sources
- Estimates potential cohort sizes
- Assesses data quality metrics

#### EHR Connector (8242)
- Interfaces with EHR systems
- Extracts clinical data
- Queries patient records

#### Claims Parser (8243)
- Processes insurance claims data
- Analyzes healthcare costs
- Identifies procedures and diagnoses

#### Site Feasibility Predictor (8244)
- Predicts site performance
- Assesses site capabilities
- Estimates enrollment rates

#### Diversity Mapper (8245)
- Calculates diversity indices
- Maps demographic distributions
- Assesses population representation

#### Protocol Scorer (8246)
- Analyzes protocol complexity
- Identifies potential challenges
- Provides optimization recommendations

#### SoA Comparator (8247)
- Compares study schedules
- Analyzes patient and site burden
- Suggests visit optimizations

## Data Flow

1. **User Input**: Frontend collects study parameters
2. **Request Routing**: Frontend sends POST to Orchestrator
3. **Service Orchestration**: 
   - Protocol complexity assessed first
   - Data sources identified in parallel
   - Site feasibility calculated per country
   - Results aggregated and ranked
4. **Response Synthesis**: Combined results sent to frontend
5. **Visualization**: Frontend displays interactive results

## Communication Patterns

### Synchronous Communication
- REST APIs for all service interactions
- JSON payloads for data exchange
- HTTP status codes for error signaling

### Asynchronous Patterns
- Async/await for non-blocking I/O
- Parallel service calls using asyncio.gather()
- Future: Message queue integration for long-running tasks

## Scalability Considerations

### Horizontal Scaling
- Each service can be scaled independently
- Stateless design enables easy replication
- Load balancer distribution (Azure App Service)

### Performance Optimization
- Service-level caching
- Connection pooling for HTTP clients
- Lazy loading of heavy dependencies
- Database connection optimization (future)

## Security Architecture

### Authentication & Authorization
- Azure AD integration (production)
- Service-to-service authentication via managed identities
- API key management through Azure Key Vault

### Data Protection
- HTTPS for all communications
- Encryption at rest (Azure storage)
- No PII storage in logs
- Input validation and sanitization

## Deployment Architecture

### Local Development
- Docker Compose for service orchestration
- Hot reload for rapid development
- Isolated service testing

### Production (Azure)
- Azure Container Registry for image storage
- Azure App Service for container hosting
- Azure Key Vault for secrets
- Azure Application Gateway for load balancing

## Monitoring & Observability

### Logging
- Structured JSON logging
- Correlation IDs for request tracing
- Log aggregation to Azure Log Analytics

### Metrics
- Request/response times
- Service health status
- Error rates and types
- Resource utilization

### Alerting
- Service health alerts
- Performance degradation notifications
- Error rate thresholds

## Disaster Recovery

### Backup Strategy
- Container images in ACR with geo-replication
- Configuration backups in source control
- Database backups (when implemented)

### Recovery Procedures
- Automated rollback on deployment failure
- Blue-green deployment support
- Service health checks and auto-restart

## Future Enhancements

### Planned Features
1. **Database Integration**: PostgreSQL for persistent storage
2. **Caching Layer**: Redis for performance optimization
3. **Message Queue**: Azure Service Bus for async processing
4. **API Gateway**: Azure API Management for advanced routing
5. **Machine Learning**: Azure ML for predictive analytics
6. **Real dcri-mcp-tools Integration**: Replace mocks with actual tool calls

### Architectural Improvements
- Event-driven architecture with Event Grid
- GraphQL API layer for flexible querying
- WebSocket support for real-time updates
- Multi-region deployment for global availability