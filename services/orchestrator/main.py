from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import httpx
import asyncio
import os

app = FastAPI(title="RWE Study Planner Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs - using Docker service names for internal networking
# In production, these would be environment variables pointing to Azure endpoints
MCP_SERVICES = {
    "data_ingestor": os.getenv("DATA_INGESTOR_URL", "http://mcp_dataingestor:8240"),
    "ehr_connector": os.getenv("EHR_CONNECTOR_URL", "http://mcp_ehrconnector:8240"),
    "claims_parser": os.getenv("CLAIMS_PARSER_URL", "http://mcp_claimsparser:8240"),
    "feasibility_predictor": os.getenv("FEASIBILITY_URL", "http://mcp_feasibility:8240"),
    "diversity_mapper": os.getenv("DIVERSITY_URL", "http://mcp_diversity:8240"),
    "protocol_scorer": os.getenv("PROTOCOL_URL", "http://mcp_protocolscorer:8240"),
    "soa_comparator": os.getenv("SOA_URL", "http://mcp_soacomparator:8240")
}

class RWEStudyRequest(BaseModel):
    protocol_text: str
    disease_area: str
    target_countries: List[str]
    target_enrollment: int
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    study_duration_months: int
    primary_endpoints: List[str]
    secondary_endpoints: List[str]

class SiteRecommendation(BaseModel):
    site_id: str
    site_name: str
    country: str
    feasibility_score: float
    diversity_score: float
    data_availability_score: float
    overall_rank: int
    strengths: List[str]
    challenges: List[str]

class RWEStudyPlan(BaseModel):
    study_id: str
    protocol_complexity_score: float
    estimated_total_cohort_size: int
    recommended_sites: List[SiteRecommendation]
    data_sources: List[Dict]
    timeline_estimate: Dict
    risk_factors: List[str]
    optimization_opportunities: List[str]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchestrator", "timestamp": datetime.now().isoformat()}

@app.get("/service_status")
async def check_service_status():
    """Check health status of all MCP services"""
    status = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, url in MCP_SERVICES.items():
            try:
                response = await client.get(f"{url}/health")
                status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                status[service_name] = "unreachable"
    return status

@app.post("/plan_rwe_study", response_model=RWEStudyPlan)
async def plan_rwe_study(request: RWEStudyRequest):
    """Main orchestration endpoint that coordinates all MCP services"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Assess Protocol Complexity
            protocol_response = await client.post(
                f"{MCP_SERVICES['protocol_scorer']}/score",
                json={"protocol_text": request.protocol_text}
            )
            protocol_complexity = protocol_response.json()
            
            # Step 2: Identify Data Sources (parallel calls)
            data_source_task = client.post(
                f"{MCP_SERVICES['data_ingestor']}/identify_sources",
                json={
                    "disease_area": request.disease_area,
                    "geography": request.target_countries,
                    "minimum_patient_count": request.target_enrollment
                }
            )
            
            # Step 3: Estimate Cohort Size
            cohort_task = client.post(
                f"{MCP_SERVICES['data_ingestor']}/estimate_cohort_size",
                json={
                    "base_population": 100000,
                    "inclusion_criteria": request.inclusion_criteria,
                    "exclusion_criteria": request.exclusion_criteria
                }
            )
            
            # Execute parallel tasks
            data_sources_response, cohort_response = await asyncio.gather(
                data_source_task, cohort_task
            )
            
            data_sources = data_sources_response.json()
            cohort_estimate = cohort_response.json()
            
            # Step 4: Assess Site Feasibility for each country
            site_recommendations = []
            for country in request.target_countries:
                # Parallel calls for feasibility and diversity
                feasibility_task = client.post(
                    f"{MCP_SERVICES['feasibility_predictor']}/predict_feasibility",
                    json={
                        "country": country,
                        "protocol_complexity": protocol_complexity["overall_score"],
                        "target_enrollment": request.target_enrollment
                    }
                )
                
                diversity_task = client.post(
                    f"{MCP_SERVICES['diversity_mapper']}/calculate_diversity",
                    json={"country": country}
                )
                
                feasibility_resp, diversity_resp = await asyncio.gather(
                    feasibility_task, diversity_task
                )
                
                # Create site recommendations
                for i in range(3):  # Mock 3 sites per country
                    site = SiteRecommendation(
                        site_id=f"{country}_SITE_{i+1:03d}",
                        site_name=f"{country} Clinical Research Site {i+1}",
                        country=country,
                        feasibility_score=8.5 - (i * 0.3),
                        diversity_score=7.8 - (i * 0.2),
                        data_availability_score=8.0 - (i * 0.1),
                        overall_rank=len(site_recommendations) + 1,
                        strengths=[
                            "Strong enrollment history",
                            "Experienced research staff",
                            "Good data quality"
                        ][:2-i],
                        challenges=[
                            "Limited parking",
                            "Competition from other studies"
                        ][i:i+1]
                    )
                    site_recommendations.append(site)
            
            # Step 5: Compare Schedule of Assessments
            soa_response = await client.post(
                f"{MCP_SERVICES['soa_comparator']}/analyze_burden",
                json={
                    "study_duration_months": request.study_duration_months,
                    "endpoints": request.primary_endpoints + request.secondary_endpoints
                }
            )
            
            # Sort sites by overall score
            site_recommendations.sort(
                key=lambda x: (x.feasibility_score + x.diversity_score + x.data_availability_score) / 3,
                reverse=True
            )
            
            # Update rankings
            for idx, site in enumerate(site_recommendations):
                site.overall_rank = idx + 1
            
            # Compile final study plan
            study_plan = RWEStudyPlan(
                study_id=f"RWE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                protocol_complexity_score=protocol_complexity["overall_score"],
                estimated_total_cohort_size=cohort_estimate["estimated_cohort_size"],
                recommended_sites=site_recommendations[:10],  # Top 10 sites
                data_sources=data_sources[:5],  # Top 5 data sources
                timeline_estimate={
                    "startup_months": 3,
                    "enrollment_months": request.study_duration_months,
                    "total_months": request.study_duration_months + 6
                },
                risk_factors=protocol_complexity.get("warnings", []),
                optimization_opportunities=protocol_complexity.get("recommendations", [])
            )
            
            return study_plan
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service communication error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration error: {str(e)}")

@app.post("/quick_assessment")
async def quick_assessment(data: Dict):
    """Lightweight assessment endpoint for quick protocol review"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Just check protocol complexity
            response = await client.post(
                f"{MCP_SERVICES['protocol_scorer']}/score",
                json={"protocol_text": data.get("protocol_text", "")}
            )
            
            return {
                "assessment": "quick",
                "complexity": response.json(),
                "recommendation": "Proceed with full planning" if response.json()["overall_score"] < 7 else "Consider protocol simplification first"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8240)