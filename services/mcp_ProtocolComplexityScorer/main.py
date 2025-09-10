from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import httpx
import json

app = FastAPI(title="Protocol Complexity Scorer MCP Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProtocolInput(BaseModel):
    protocol_text: str
    protocol_sections: Optional[Dict] = None
    analysis_depth: Optional[str] = "standard"

class ComplexityScore(BaseModel):
    overall_score: float
    complexity_factors: Dict
    warnings: List[str]
    recommendations: List[str]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp_ProtocolComplexityScorer"}

@app.post("/score", response_model=ComplexityScore)
async def score_protocol(data: ProtocolInput):
    try:
        # Mock complexity scoring logic
        # In production, this would call the actual dcri-mcp-tools API
        
        text_length = len(data.protocol_text)
        
        # Calculate complexity factors
        complexity_factors = {
            "length_score": min(text_length / 10000, 10),
            "procedures_complexity": 6.5,
            "inclusion_criteria_complexity": 7.2,
            "data_collection_complexity": 5.8,
            "visit_schedule_complexity": 6.0
        }
        
        # Calculate overall score (weighted average)
        overall_score = sum(complexity_factors.values()) / len(complexity_factors)
        
        # Generate warnings based on complexity
        warnings = []
        if complexity_factors["length_score"] > 8:
            warnings.append("Protocol document is very lengthy")
        if complexity_factors["procedures_complexity"] > 7:
            warnings.append("Complex procedures may impact site feasibility")
        if complexity_factors["inclusion_criteria_complexity"] > 7:
            warnings.append("Stringent inclusion criteria may affect enrollment")
            
        # Generate recommendations
        recommendations = []
        if overall_score > 7:
            recommendations.append("Consider simplifying protocol procedures")
            recommendations.append("Review inclusion/exclusion criteria for potential relaxation")
        if complexity_factors["visit_schedule_complexity"] > 6:
            recommendations.append("Consider reducing visit frequency or combining assessments")
            
        return ComplexityScore(
            overall_score=round(overall_score, 2),
            complexity_factors=complexity_factors,
            warnings=warnings,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_sections")
async def analyze_protocol_sections(data: Dict):
    try:
        # Analyze specific protocol sections
        section_analysis = {
            "objectives": {"complexity": 5.2, "clarity": 8.1},
            "endpoints": {"primary_count": 1, "secondary_count": 5, "complexity": 6.3},
            "eligibility": {"inclusion_count": 12, "exclusion_count": 18, "restrictiveness": 7.5},
            "procedures": {"invasive_count": 3, "non_invasive_count": 8, "burden_score": 6.8}
        }
        
        return {
            "section_analysis": section_analysis,
            "high_complexity_areas": ["eligibility", "procedures"],
            "optimization_opportunities": [
                "Consolidate secondary endpoints",
                "Review exclusion criteria necessity"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8240)