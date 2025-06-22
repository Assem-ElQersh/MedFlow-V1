from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import random
import json
import time

app = FastAPI(title="MedFlow AI Service", version="1.0.0")

class SymptomAnalysisRequest(BaseModel):
    symptoms: List[str]
    medical_history: Optional[List[str]] = None
    vital_signs: Optional[Dict] = None

class SymptomAnalysisResponse(BaseModel):
    triage_level: str
    triage_score: float
    assessment: Dict
    recommendations: List[str]
    confidence: float

class ImageAnalysisRequest(BaseModel):
    image_path: str
    image_type: str

class ImageAnalysisResponse(BaseModel):
    analysis: Dict
    confidence_score: float
    findings: List[str]
    recommendations: List[str]
    requires_review: bool

class DifferentialDiagnosisRequest(BaseModel):
    symptoms: List[str]
    patient_history: Optional[Dict] = None
    exam_findings: Optional[List[str]] = None

class DifferentialDiagnosisResponse(BaseModel):
    diagnoses: List[Dict]
    reasoning: str
    confidence: float

# Mock medical knowledge for realistic responses
SYMPTOM_TRIAGE_RULES = {
    "chest pain": {"level": "critical", "score": 0.9},
    "difficulty breathing": {"level": "critical", "score": 0.85},
    "severe headache": {"level": "urgent", "score": 0.7},
    "fever": {"level": "urgent", "score": 0.6},
    "nausea": {"level": "routine", "score": 0.3},
    "cough": {"level": "routine", "score": 0.4},
    "fatigue": {"level": "routine", "score": 0.2},
    "dizziness": {"level": "urgent", "score": 0.5},
    "abdominal pain": {"level": "urgent", "score": 0.6},
    "shortness of breath": {"level": "critical", "score": 0.8}
}

IMAGE_ANALYSIS_TEMPLATES = {
    "xray": {
        "normal": {
            "findings": ["Clear lung fields", "Normal cardiac silhouette", "No acute findings"],
            "confidence": 0.92,
            "requires_review": False
        },
        "pneumonia": {
            "findings": ["Consolidation in right lower lobe", "Possible infectious process"],
            "confidence": 0.78,
            "requires_review": True
        },
        "fracture": {
            "findings": ["Possible fracture line visible", "Bone displacement noted"],
            "confidence": 0.85,
            "requires_review": True
        }
    },
    "skin": {
        "normal": {
            "findings": ["Normal skin appearance", "No concerning lesions"],
            "confidence": 0.88,
            "requires_review": False
        },
        "suspicious": {
            "findings": ["Irregular pigmentation", "Asymmetric borders", "Requires dermatology review"],
            "confidence": 0.72,
            "requires_review": True
        }
    }
}

@app.get("/")
async def root():
    return {"message": "MedFlow AI Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-service"}

@app.post("/ai/analyze-symptoms", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(request: SymptomAnalysisRequest):
    """
    Mock implementation of MedGemma 27B Text-Only analysis
    In production, this would interface with the actual MedGemma model
    """
    # Simulate processing time
    time.sleep(random.uniform(0.5, 2.0))
    
    # Calculate triage based on symptoms
    max_score = 0
    triage_level = "routine"
    
    for symptom in request.symptoms:
        symptom_lower = symptom.lower()
        for key, value in SYMPTOM_TRIAGE_RULES.items():
            if key in symptom_lower:
                if value["score"] > max_score:
                    max_score = value["score"]
                    triage_level = value["level"]
    
    # Adjust score based on medical history
    if request.medical_history:
        for condition in request.medical_history:
            if any(term in condition.lower() for term in ["diabetes", "heart", "hypertension"]):
                max_score = min(max_score + 0.1, 1.0)
    
    # Generate assessment
    assessment = {
        "primary_concern": request.symptoms[0] if request.symptoms else "General consultation",
        "risk_factors": request.medical_history or [],
        "clinical_reasoning": f"Based on reported symptoms and medical history, patient presents with {triage_level} priority case.",
        "red_flags": [s for s in request.symptoms if any(flag in s.lower() for flag in ["chest pain", "difficulty breathing", "severe"])]
    }
    
    # Generate recommendations
    recommendations = []
    if triage_level == "critical":
        recommendations = [
            "Immediate medical attention required",
            "Consider emergency department evaluation",
            "Monitor vital signs closely"
        ]
    elif triage_level == "urgent":
        recommendations = [
            "Schedule appointment within 24-48 hours",
            "Monitor symptoms for worsening",
            "Return if symptoms deteriorate"
        ]
    else:
        recommendations = [
            "Routine follow-up appropriate",
            "Self-care measures may be sufficient",
            "Schedule if symptoms persist"
        ]
    
    return SymptomAnalysisResponse(
        triage_level=triage_level,
        triage_score=max_score,
        assessment=assessment,
        recommendations=recommendations,
        confidence=random.uniform(0.7, 0.95)
    )

@app.post("/ai/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Mock implementation of MedGemma 4B Multimodal analysis
    In production, this would interface with the actual MedGemma model
    """
    # Simulate processing time
    time.sleep(random.uniform(1.0, 3.0))
    
    # Get template based on image type
    templates = IMAGE_ANALYSIS_TEMPLATES.get(request.image_type, IMAGE_ANALYSIS_TEMPLATES["xray"])
    
    # Randomly select a finding type (in production, this would be AI analysis)
    finding_type = random.choice(list(templates.keys()))
    template = templates[finding_type]
    
    analysis = {
        "image_type": request.image_type,
        "quality_assessment": "Good image quality, adequate for interpretation",
        "anatomical_structures": ["Clearly visible", "Adequate positioning"],
        "pathological_findings": template["findings"],
        "technical_factors": "Appropriate exposure and positioning"
    }
    
    # Generate recommendations based on findings
    recommendations = []
    if template["requires_review"]:
        recommendations = [
            "Radiologist review recommended",
            "Clinical correlation advised",
            "Follow-up imaging may be needed"
        ]
    else:
        recommendations = [
            "No immediate follow-up required",
            "Continue current management",
            "Repeat if clinically indicated"
        ]
    
    return ImageAnalysisResponse(
        analysis=analysis,
        confidence_score=template["confidence"],
        findings=template["findings"],
        recommendations=recommendations,
        requires_review=template["requires_review"]
    )

@app.post("/ai/differential-diagnosis", response_model=DifferentialDiagnosisResponse)
async def generate_differential_diagnosis(request: DifferentialDiagnosisRequest):
    """
    Mock implementation of MedGemma 27B differential diagnosis generation
    """
    # Simulate processing time
    time.sleep(random.uniform(1.5, 3.5))
    
    # Mock differential diagnoses based on symptoms
    common_diagnoses = {
        "chest pain": [
            {"diagnosis": "Myocardial Infarction", "probability": 0.15, "urgency": "critical"},
            {"diagnosis": "Angina Pectoris", "probability": 0.25, "urgency": "urgent"},
            {"diagnosis": "Costochondritis", "probability": 0.30, "urgency": "routine"},
            {"diagnosis": "GERD", "probability": 0.20, "urgency": "routine"},
            {"diagnosis": "Pulmonary Embolism", "probability": 0.10, "urgency": "critical"}
        ],
        "fever": [
            {"diagnosis": "Viral Upper Respiratory Infection", "probability": 0.40, "urgency": "routine"},
            {"diagnosis": "Bacterial Pneumonia", "probability": 0.20, "urgency": "urgent"},
            {"diagnosis": "Urinary Tract Infection", "probability": 0.15, "urgency": "urgent"},
            {"diagnosis": "Influenza", "probability": 0.25, "urgency": "routine"}
        ],
        "headache": [
            {"diagnosis": "Tension Headache", "probability": 0.50, "urgency": "routine"},
            {"diagnosis": "Migraine", "probability": 0.30, "urgency": "routine"},
            {"diagnosis": "Cluster Headache", "probability": 0.10, "urgency": "urgent"},
            {"diagnosis": "Secondary Headache", "probability": 0.10, "urgency": "urgent"}
        ]
    }
    
    # Find relevant diagnoses
    diagnoses = []
    for symptom in request.symptoms:
        symptom_lower = symptom.lower()
        for key, diagnosis_list in common_diagnoses.items():
            if key in symptom_lower:
                diagnoses.extend(diagnosis_list)
                break
    
    # Default if no specific matches
    if not diagnoses:
        diagnoses = [
            {"diagnosis": "Viral Syndrome", "probability": 0.40, "urgency": "routine"},
            {"diagnosis": "General Medical Consultation", "probability": 0.60, "urgency": "routine"}
        ]
    
    # Sort by probability
    diagnoses.sort(key=lambda x: x["probability"], reverse=True)
    
    reasoning = f"""
    Based on the presented symptoms: {', '.join(request.symptoms)}
    
    Clinical reasoning:
    - Pattern recognition suggests multiple possible etiologies
    - Symptom constellation analyzed against medical knowledge base
    - Risk stratification performed considering patient history
    - Differential prioritized by likelihood and clinical urgency
    
    Recommendation: Further clinical evaluation and targeted diagnostics as indicated.
    """
    
    return DifferentialDiagnosisResponse(
        diagnoses=diagnoses[:5],  # Return top 5
        reasoning=reasoning.strip(),
        confidence=random.uniform(0.75, 0.92)
    )

@app.get("/ai/models/status")
async def get_model_status():
    """Return the status of AI models"""
    return {
        "medgemma_27b_text": {
            "status": "loaded",
            "model_type": "text-only",
            "capabilities": ["symptom_analysis", "differential_diagnosis", "treatment_recommendations"],
            "last_updated": "2024-01-15T10:00:00Z"
        },
        "medgemma_4b_multimodal": {
            "status": "loaded", 
            "model_type": "multimodal",
            "capabilities": ["image_analysis", "report_generation", "image_text_correlation"],
            "last_updated": "2024-01-15T10:00:00Z"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 