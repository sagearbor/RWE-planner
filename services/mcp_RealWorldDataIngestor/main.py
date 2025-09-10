from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import random

app = FastAPI(title="Real World Data Ingestor MCP Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DataSourceQuery(BaseModel):
    disease_area: str
    geography: Optional[List[str]] = None
    data_types: Optional[List[str]] = ["EHR", "Claims"]
    minimum_patient_count: Optional[int] = 100

class DataSource(BaseModel):
    source_id: str
    source_name: str
    data_type: str
    geography: str
    patient_count: int
    last_updated: str
    quality_score: float
    availability: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp_RealWorldDataIngestor"}

@app.post("/identify_sources", response_model=List[DataSource])
async def identify_data_sources(query: DataSourceQuery):
    try:
        # Mock data source identification
        # In production, this would query actual data source registries
        
        mock_sources = []
        geographies = query.geography or ["USA", "UK", "Germany", "Japan"]
        
        for geo in geographies:
            for data_type in query.data_types:
                patient_count = random.randint(query.minimum_patient_count, 50000)
                quality_score = round(random.uniform(7.0, 9.5), 1)
                
                source = DataSource(
                    source_id=f"{geo}_{data_type}_{random.randint(100, 999)}",
                    source_name=f"{geo} National {data_type} Database",
                    data_type=data_type,
                    geography=geo,
                    patient_count=patient_count,
                    last_updated=datetime.now().isoformat(),
                    quality_score=quality_score,
                    availability="Available" if quality_score > 7.5 else "Limited"
                )
                mock_sources.append(source)
        
        # Sort by patient count and quality score
        mock_sources.sort(key=lambda x: (x.patient_count, x.quality_score), reverse=True)
        
        return mock_sources
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/estimate_cohort_size")
async def estimate_cohort_size(data: Dict):
    try:
        # Estimate potential cohort size based on inclusion/exclusion criteria
        base_population = data.get("base_population", 100000)
        inclusion_criteria = data.get("inclusion_criteria", [])
        exclusion_criteria = data.get("exclusion_criteria", [])
        
        # Apply mock filters (in reality would use actual data queries)
        estimated_size = base_population
        
        # Apply inclusion criteria reductions
        for _ in inclusion_criteria:
            estimated_size *= random.uniform(0.3, 0.8)
            
        # Apply exclusion criteria reductions  
        for _ in exclusion_criteria:
            estimated_size *= random.uniform(0.7, 0.95)
            
        return {
            "estimated_cohort_size": int(estimated_size),
            "confidence_interval": {
                "lower": int(estimated_size * 0.8),
                "upper": int(estimated_size * 1.2)
            },
            "factors_considered": {
                "inclusion_criteria_count": len(inclusion_criteria),
                "exclusion_criteria_count": len(exclusion_criteria),
                "base_population": base_population
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data_quality_assessment")
async def assess_data_quality(data: Dict):
    try:
        source_id = data.get("source_id", "unknown")
        
        # Mock data quality metrics
        quality_metrics = {
            "completeness": round(random.uniform(85, 98), 1),
            "accuracy": round(random.uniform(88, 96), 1),
            "timeliness": round(random.uniform(90, 99), 1),
            "consistency": round(random.uniform(87, 95), 1),
            "validity": round(random.uniform(89, 97), 1)
        }
        
        overall_quality = sum(quality_metrics.values()) / len(quality_metrics)
        
        return {
            "source_id": source_id,
            "quality_metrics": quality_metrics,
            "overall_quality_score": round(overall_quality, 1),
            "recommendations": [
                "Data quality is suitable for RWE studies" if overall_quality > 90 
                else "Consider data cleaning and validation procedures"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8240)