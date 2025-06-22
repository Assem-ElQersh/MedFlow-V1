from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx
import os

app = FastAPI(title="MedFlow Clinical Service", version="1.0.0")

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")

class DiagnosisRequest(BaseModel):
    symptoms: List[str]
    patient_history: Optional[Dict] = None
    exam_findings: Optional[List[str]] = None

class DiagnosisResponse(BaseModel):
    diagnoses: List[Dict]
    reasoning: str
    confidence: float

@app.get("/")
async def root():
    return {"message": "MedFlow Clinical Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "clinical-service"}

@app.post("/clinical/diagnosis", response_model=DiagnosisResponse)
async def generate_diagnosis(request: DiagnosisRequest):
    """Generate differential diagnosis using AI service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/ai/differential-diagnosis",
                json=request.dict(),
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="AI service unavailable")
            
            return response.json()
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI service timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnosis generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 