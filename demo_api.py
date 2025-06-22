from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union
import uvicorn
import json
import os

# Import our simple Gradio MedGemma service
try:
    from gradio_medgemma_service import GradioMedGemmaService
    REAL_MEDGEMMA_AVAILABLE = True
except ImportError:
    REAL_MEDGEMMA_AVAILABLE = False
    print("⚠️ Gradio MedGemma service not available - using demo mode")

app = FastAPI(title="MedFlow AI - Real MedGemma Gateway", version="2.0.0")

# Initialize simple Gradio MedGemma service
medgemma_service = None
if REAL_MEDGEMMA_AVAILABLE:
    try:
        medgemma_service = GradioMedGemmaService()
        print("🚀 Live MedGemma demo service ready!")
    except Exception as e:
        print(f"⚠️ Failed to connect to live demo: {str(e)}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo data models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# Demo credentials (from the README)
DEMO_USERS = {
    "patient@demo.com": {
        "password": "password123",
        "role": "patient",
        "full_name": "Demo Patient",
        "id": 1
    },
    "doctor@demo.com": {
        "password": "password123", 
        "role": "physician",
        "full_name": "Dr. Demo",
        "id": 2
    }
}

@app.get("/")
async def root():
    return {"message": "MedFlow AI Demo API Gateway", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "demo-api-gateway"}

@app.post("/auth/login")
async def login(request: Request):
    try:
        # Get content type
        content_type = request.headers.get("content-type", "")
        username = None
        password = None
        
        if "application/json" in content_type:
            # Handle JSON data
            body = await request.json()
            if "username" in body:
                username = body["username"]
                password = body["password"]
            elif "email" in body:
                username = body["email"]
                password = body["password"]
        elif "application/x-www-form-urlencoded" in content_type:
            # Handle form data
            form = await request.form()
            username = form.get("username") or form.get("email")
            password = form.get("password")
        else:
            # Try both formats
            try:
                body = await request.json()
                username = body.get("username") or body.get("email")
                password = body.get("password")
            except:
                form = await request.form()
                username = form.get("username") or form.get("email")
                password = form.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username/email and password required")
        
        # Check demo credentials
        if username in DEMO_USERS and DEMO_USERS[username]["password"] == password:
            user_data = DEMO_USERS[username]
            return {
                "access_token": f"demo_token_{user_data['id']}",
                "token_type": "bearer",
                "user": {
                    "id": user_data["id"],
                    "email": username,
                    "full_name": user_data["full_name"],
                    "role": user_data["role"]
                }
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login error: {str(e)}")

# Alternative login endpoint for OAuth2PasswordRequestForm (FastAPI standard)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

@app.post("/auth/token")
async def login_oauth(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    
    # Check demo credentials
    if username in DEMO_USERS and DEMO_USERS[username]["password"] == password:
        user_data = DEMO_USERS[username]
        return {
            "access_token": f"demo_token_{user_data['id']}",
            "token_type": "bearer",
            "user": {
                "id": user_data["id"],
                "email": username,
                "full_name": user_data["full_name"],
                "role": user_data["role"]
            }
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

@app.get("/auth/me")
async def get_current_user():
    # Demo user info
    return {
        "id": 1,
        "email": "patient@demo.com",
        "full_name": "Demo Patient",
        "role": "patient"
    }

@app.get("/consultations")
async def get_consultations():
    # Demo consultation data
    return [
        {
            "id": 1,
            "symptoms": "Headache, fever",
            "triage_level": "MODERATE",
            "triage_score": 65,
            "status": "PENDING",
            "created_at": "2025-06-22T12:00:00Z"
        }
    ]

@app.post("/consultations")
async def create_consultation(consultation_data: dict):
    # Demo consultation creation
    return {
        "id": 2,
        "symptoms": consultation_data.get("symptoms", ""),
        "triage_level": "LOW",
        "triage_score": 30,
        "status": "PENDING",
        "created_at": "2025-06-22T15:30:00Z"
    }

@app.post("/images/upload")
async def upload_image(request: Request):
    # Real MedGemma-powered image upload handler
    try:
        form = await request.form()
        image_file = form.get("file") or form.get("image")
        image_type = form.get("image_type", "X-Ray")
        
        if not image_file:
            raise HTTPException(status_code=400, detail="No image file provided")
        
        # Use live MedGemma demo if available, otherwise fallback to simulation
        if medgemma_service:
            print("🚀 Using LIVE MedGemma demo for analysis...")
            medgemma_analysis = await medgemma_service.analyze_medical_image(image_file, image_type)
            ai_model = "MedGemma 4B IT (Live Demo)"
            message = "Image analyzed using LIVE MedGemma AI demo!"
        else:
            print("📋 Using demo MedGemma simulation...")
            medgemma_analysis = analyze_with_medgemma(image_type)
            ai_model = "MedGemma 4B Multimodal (Demo)"
            message = "Image analyzed using demo MedGemma simulation."
        
        return {
            "id": 123,
            "filename": f"medgemma_real_{image_type.lower()}.jpeg",
            "image_type": image_type,
            "status": "analyzed",
            "ai_model": ai_model,
            "analysis": medgemma_analysis,
            "uploaded_at": "2025-06-22T15:30:00Z",
            "message": message
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"MedGemma analysis failed: {str(e)}"
        }

def analyze_with_medgemma(image_type):
    """Simulate MedGemma AI analysis based on image type"""
    
    if image_type.lower() in ["x-ray", "chest x-ray", "chest"]:
        return {
            "model": "MedGemma 4B Multimodal",
            "confidence": 91.3,
            "findings": [
                "MedGemma Analysis: Normal chest radiograph",
                "Cardiomediastinal silhouette within normal limits",
                "No acute pulmonary infiltrates or pleural effusions",
                "Bony structures appear intact",
                "No suspicious masses or nodules detected"
            ],
            "priority": "LOW",
            "recommendation": "MedGemma suggests routine clinical correlation. No immediate intervention required.",
            "technical_details": {
                "image_quality": "Good",
                "artifacts": None,
                "comparison": "No prior studies available for comparison"
            }
        }
    elif image_type.lower() in ["ct", "ct scan", "computed tomography"]:
        return {
            "model": "MedGemma 4B Multimodal", 
            "confidence": 87.6,
            "findings": [
                "MedGemma CT Analysis: No acute intracranial abnormalities",
                "Gray-white matter differentiation preserved",
                "No evidence of hemorrhage or mass effect",
                "Ventricular system normal in size and configuration"
            ],
            "priority": "LOW",
            "recommendation": "MedGemma: Normal CT findings. Clinical correlation recommended.",
            "technical_details": {
                "slice_thickness": "5mm",
                "contrast": "Non-contrast study",
                "quality": "Diagnostic"
            }
        }
    elif image_type.lower() in ["mri", "magnetic resonance"]:
        return {
            "model": "MedGemma 4B Multimodal",
            "confidence": 89.2,
            "findings": [
                "MedGemma MRI Analysis: Normal brain MRI",
                "No abnormal signal intensity on T1 and T2 sequences",
                "No restricted diffusion on DWI",
                "Vascular structures appear normal"
            ],
            "priority": "LOW", 
            "recommendation": "MedGemma: Unremarkable MRI study. Continue clinical management as appropriate.",
            "technical_details": {
                "sequences": ["T1", "T2", "FLAIR", "DWI"],
                "field_strength": "1.5T",
                "quality": "Excellent"
            }
        }
    elif image_type.lower() in ["dermatology", "skin", "dermoscopy"]:
        return {
            "model": "MedGemma 4B Multimodal",
            "confidence": 93.1,
            "findings": [
                "MedGemma Dermatology Analysis: Benign-appearing lesion",
                "Regular borders and uniform pigmentation",
                "No asymmetry or irregular features",
                "Consistent with seborrheic keratosis pattern"
            ],
            "priority": "LOW",
            "recommendation": "MedGemma: Benign characteristics. Routine dermatological follow-up recommended.",
            "technical_details": {
                "dermoscopy_features": "Regular pattern",
                "color_analysis": "Uniform brown pigmentation",
                "border_assessment": "Well-defined"
            }
        }
    else:
        return {
            "model": "MedGemma 4B Multimodal",
            "confidence": 82.4,
            "findings": [
                "MedGemma General Analysis: Image quality adequate for interpretation",
                "No obvious acute abnormalities detected",
                "Recommend specialist correlation for detailed assessment"
            ],
            "priority": "MODERATE",
            "recommendation": "MedGemma: Requires specialist interpretation based on clinical context.",
            "technical_details": {
                "image_type": image_type,
                "analysis_mode": "General medical imaging",
                "note": "Specialized analysis available with domain-specific models"
            }
        }

@app.get("/triage/queue")
async def get_triage_queue():
    # Demo triage queue
    return [
        {
            "id": 1,
            "patient_name": "Demo Patient",
            "triage_level": "MODERATE",
            "triage_score": 65,
            "symptoms": "Headache, fever",
            "wait_time": "15 minutes",
            "status": "WAITING"
        },
        {
            "id": 2,
            "patient_name": "John Doe",
            "triage_level": "LOW",
            "triage_score": 30,
            "symptoms": "Minor cut",
            "wait_time": "45 minutes", 
            "status": "WAITING"
        }
    ]

@app.get("/triage/stats")
async def get_triage_stats():
    # Demo triage statistics
    return {
        "total_patients": 12,
        "high_priority": 1,
        "moderate_priority": 3,
        "low_priority": 8,
        "average_wait_time": "28 minutes",
        "beds_available": 5,
        "staff_on_duty": 8
    }

@app.get("/services/status")
async def get_services_status():
    # Determine if MedGemma service is running
    medgemma_status = "healthy" if medgemma_service else "demo_mode"
    
    return {
        "api_gateway": {"status": "healthy"},
        "frontend": {"status": "healthy"},
        "database": {"status": "demo_mode"},
        "ai_service": {"status": medgemma_status},
        "imaging_service": {"status": "healthy"},
        "medgemma_service": {"status": medgemma_status}
    }

@app.get("/images/{image_id}/analysis")
async def get_image_analysis(image_id: str):
    # MedGemma analysis results endpoint
    return {
        "image_id": image_id,
        "status": "completed",
        "ai_model": "MedGemma 4B Multimodal",
        "analysis": {
            "model": "MedGemma 4B Multimodal",
            "confidence": 91.3,
            "findings": [
                "🔬 MedGemma Analysis: Normal chest radiograph", 
                "💚 Cardiomediastinal silhouette within normal limits",
                "✅ No acute pulmonary infiltrates or pleural effusions",
                "🦴 Bony structures appear intact",
                "🔍 No suspicious masses or nodules detected"
            ],
            "priority": "LOW",
            "recommendation": "MedGemma suggests routine clinical correlation. No immediate intervention required.",
            "technical_details": {
                "image_quality": "Good",
                "artifacts": None,
                "comparison": "No prior studies available for comparison",
                "processing_time": "2.3 seconds"
            }
        },
        "analyzed_at": "2025-06-22T15:30:00Z",
        "ai_provider": "Google DeepMind MedGemma"
    }

if __name__ == "__main__":
    print("🏥 Starting MedFlow Demo API Gateway...")
    print("🤖 Powered by Google MedGemma AI for Medical Analysis")
    print("📊 Demo Credentials:")
    print("   Patient: patient@demo.com / password123")
    print("   Doctor:  doctor@demo.com / password123")
    print("🌐 API will be available at: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000) 