from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="MedFlow Patient Service", version="1.0.0")

class PatientInfo(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    medical_history: Optional[List[str]] = None

@app.get("/")
async def root():
    return {"message": "MedFlow Patient Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "patient-service"}

@app.get("/patients/{patient_id}", response_model=PatientInfo)
async def get_patient(patient_id: int):
    # Mock patient data
    return PatientInfo(
        id=patient_id,
        name="John Doe",
        email="john.doe@example.com",
        phone="+1-555-0123",
        date_of_birth="1980-01-15",
        medical_history=["Hypertension", "Type 2 Diabetes"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 