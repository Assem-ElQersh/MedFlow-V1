from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx
import os

app = FastAPI(title="MedFlow Triage Service", version="1.0.0")

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")

class TriageRequest(BaseModel):
    consultation_id: int
    symptoms: List[str]
    medical_history: Optional[List[str]] = None
    vital_signs: Optional[Dict] = None

class TriageResponse(BaseModel):
    consultation_id: int
    triage_level: str
    triage_score: float
    assessment: Dict
    recommendations: List[str]
    confidence: float

@app.get("/")
async def root():
    return {"message": "MedFlow Triage Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "triage-service"}

@app.post("/triage/analyze", response_model=TriageResponse)
async def analyze_triage(request: TriageRequest):
    """
    Analyze patient symptoms and determine triage level using AI service
    """
    try:
        # Call AI service for symptom analysis
        async with httpx.AsyncClient() as client:
            ai_request = {
                "symptoms": request.symptoms,
                "medical_history": request.medical_history,
                "vital_signs": request.vital_signs
            }
            
            response = await client.post(
                f"{AI_SERVICE_URL}/ai/analyze-symptoms",
                json=ai_request,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail="AI service unavailable"
                )
            
            ai_result = response.json()
            
            return TriageResponse(
                consultation_id=request.consultation_id,
                triage_level=ai_result["triage_level"],
                triage_score=ai_result["triage_score"],
                assessment=ai_result["assessment"],
                recommendations=ai_result["recommendations"],
                confidence=ai_result["confidence"]
            )
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="AI service timeout"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Triage analysis failed: {str(e)}"
        )

@app.get("/triage/queue")
async def get_triage_queue():
    """
    Get current triage queue (mock implementation)
    In production, this would query the database for pending consultations
    """
    return {
        "critical": [
            {"consultation_id": 1, "patient_name": "John Doe", "chief_complaint": "Chest pain", "wait_time": "0 min"},
            {"consultation_id": 5, "patient_name": "Alice Smith", "chief_complaint": "Difficulty breathing", "wait_time": "2 min"}
        ],
        "urgent": [
            {"consultation_id": 2, "patient_name": "Jane Wilson", "chief_complaint": "Severe headache", "wait_time": "15 min"},
            {"consultation_id": 6, "patient_name": "Bob Johnson", "chief_complaint": "Abdominal pain", "wait_time": "25 min"}
        ],
        "routine": [
            {"consultation_id": 3, "patient_name": "Mike Brown", "chief_complaint": "Cough", "wait_time": "45 min"},
            {"consultation_id": 4, "patient_name": "Sarah Davis", "chief_complaint": "Fatigue", "wait_time": "60 min"}
        ]
    }

@app.get("/triage/stats")
async def get_triage_stats():
    """
    Get triage statistics (mock implementation)
    """
    return {
        "total_patients": 156,
        "current_queue": 6,
        "average_wait_time": {
            "critical": "2 min",
            "urgent": "20 min", 
            "routine": "52 min"
        },
        "processed_today": 42,
        "ai_accuracy": 0.89
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 