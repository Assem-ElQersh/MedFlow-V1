from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import httpx
import sys
import os

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_database, create_tables
from shared.models import *
from shared.auth import authenticate_user, create_access_token, get_current_user, get_password_hash

app = FastAPI(title="MedFlow AI - API Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
PATIENT_SERVICE_URL = "http://patient-service:8000"
TRIAGE_SERVICE_URL = "http://triage-service:8000"
IMAGING_SERVICE_URL = "http://imaging-service:8000"
CLINICAL_SERVICE_URL = "http://clinical-service:8000"
AI_SERVICE_URL = "http://ai-service:8000"

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "MedFlow AI API Gateway", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_database)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create profile based on role
    if user.role == UserRole.PATIENT:
        patient_profile = PatientProfile(user_id=db_user.id)
        db.add(patient_profile)
        db.commit()
    elif user.role in [UserRole.PHYSICIAN, UserRole.NURSE, UserRole.SPECIALIST]:
        provider_profile = ProviderProfile(user_id=db_user.id)
        db.add(provider_profile)
        db.commit()
    
    return db_user

@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_database)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Patient service endpoints
@app.post("/patients/profile", response_model=PatientProfileResponse)
async def create_patient_profile(
    profile: PatientProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Only patients can create patient profiles")
    
    # Check if profile already exists
    existing_profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Patient profile already exists")
    
    db_profile = PatientProfile(user_id=current_user.id, **profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.get("/patients/profile", response_model=PatientProfileResponse)
async def get_patient_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Only patients can access patient profiles")
    
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return profile

# Consultation endpoints
@app.post("/consultations", response_model=ConsultationResponse)
async def create_consultation(
    consultation: ConsultationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Only patients can create consultations")
    
    # Get patient profile
    patient_profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not patient_profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    db_consultation = Consultation(
        patient_id=patient_profile.id,
        **consultation.dict()
    )
    db.add(db_consultation)
    db.commit()
    db.refresh(db_consultation)
    
    # Trigger triage analysis
    try:
        async with httpx.AsyncClient() as client:
            triage_request = TriageRequest(
                consultation_id=db_consultation.id,
                symptoms=consultation.symptoms.split(",") if consultation.symptoms else [],
                medical_history=patient_profile.medical_history.split(",") if patient_profile.medical_history else None
            )
            response = await client.post(
                f"{TRIAGE_SERVICE_URL}/triage/analyze",
                json=triage_request.dict()
            )
            if response.status_code == 200:
                triage_result = response.json()
                db_consultation.triage_level = triage_result["triage_level"]
                db_consultation.triage_score = triage_result["triage_score"]
                db_consultation.ai_assessment = str(triage_result["assessment"])
                db.commit()
    except Exception as e:
        print(f"Triage analysis failed: {e}")
    
    return db_consultation

@app.get("/consultations", response_model=List[ConsultationResponse])
async def get_consultations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    if current_user.role == UserRole.PATIENT:
        patient_profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
        if not patient_profile:
            raise HTTPException(status_code=404, detail="Patient profile not found")
        consultations = db.query(Consultation).filter(Consultation.patient_id == patient_profile.id).all()
    else:
        # Healthcare providers can see all consultations
        consultations = db.query(Consultation).all()
    
    return consultations

@app.get("/consultations/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation(
    consultation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    # Check permissions
    if current_user.role == UserRole.PATIENT:
        patient_profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
        if not patient_profile or consultation.patient_id != patient_profile.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this consultation")
    
    return consultation

# Image upload endpoint
@app.post("/images/upload")
async def upload_image(
    image_type: ImageType,
    consultation_id: int = None,
    current_user: User = Depends(get_current_user)
):
    # Forward to imaging service
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{IMAGING_SERVICE_URL}/images/upload",
            data={
                "image_type": image_type,
                "consultation_id": consultation_id,
                "user_id": current_user.id
            }
        )
        return response.json()

# Proxy endpoints for other services
@app.get("/services/status")
async def get_services_status():
    services = {
        "patient-service": PATIENT_SERVICE_URL,
        "triage-service": TRIAGE_SERVICE_URL,
        "imaging-service": IMAGING_SERVICE_URL,
        "clinical-service": CLINICAL_SERVICE_URL,
        "ai-service": AI_SERVICE_URL
    }
    
    status_results = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in services.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                status_results[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response": response.json() if response.status_code == 200 else None
                }
            except Exception as e:
                status_results[service_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }
    
    return status_results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 