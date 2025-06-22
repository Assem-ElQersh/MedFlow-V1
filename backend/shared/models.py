from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List
import json

Base = declarative_base()

# Enums
class TriageLevel(str, Enum):
    CRITICAL = "critical"
    URGENT = "urgent"
    ROUTINE = "routine"

class ImageType(str, Enum):
    XRAY = "xray"
    SKIN = "skin"
    FUNDUS = "fundus"
    CT = "ct"
    MRI = "mri"

class UserRole(str, Enum):
    PATIENT = "patient"
    PHYSICIAN = "physician"
    NURSE = "nurse"
    SPECIALIST = "specialist"
    ADMIN = "admin"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
    provider_profile = relationship("ProviderProfile", back_populates="user", uselist=False)

class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    date_of_birth = Column(DateTime)
    gender = Column(String(10))
    phone = Column(String(20))
    address = Column(Text)
    emergency_contact = Column(Text)  # JSON string
    medical_history = Column(Text)  # JSON string
    allergies = Column(Text)  # JSON string
    medications = Column(Text)  # JSON string
    
    # Relationships
    user = relationship("User", back_populates="patient_profile")
    consultations = relationship("Consultation", back_populates="patient")
    medical_images = relationship("MedicalImage", back_populates="patient")

class ProviderProfile(Base):
    __tablename__ = "provider_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    license_number = Column(String(50))
    specialty = Column(String(100))
    hospital_affiliation = Column(String(200))
    years_experience = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="provider_profile")
    consultations = relationship("Consultation", back_populates="provider")

class Consultation(Base):
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    provider_id = Column(Integer, ForeignKey("provider_profiles.id"), nullable=True)
    chief_complaint = Column(Text)
    symptoms = Column(Text)  # JSON string
    triage_level = Column(SQLEnum(TriageLevel))
    triage_score = Column(Float)
    ai_assessment = Column(Text)  # JSON string with AI analysis
    differential_diagnosis = Column(Text)  # JSON string
    treatment_plan = Column(Text)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    scheduled_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("PatientProfile", back_populates="consultations")
    provider = relationship("ProviderProfile", back_populates="consultations")
    medical_images = relationship("MedicalImage", back_populates="consultation")

class MedicalImage(Base):
    __tablename__ = "medical_images"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"))
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=True)
    filename = Column(String(255))
    original_filename = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    image_type = Column(SQLEnum(ImageType))
    ai_analysis = Column(Text)  # JSON string with AI analysis results
    confidence_score = Column(Float)
    requires_review = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("provider_profiles.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("PatientProfile", back_populates="medical_images")
    consultation = relationship("Consultation", back_populates="medical_images")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(Text)  # JSON string
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic Models for API
class UserBase(BaseModel):
    email: str
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PatientProfileBase(BaseModel):
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None

class PatientProfileCreate(PatientProfileBase):
    pass

class PatientProfileResponse(PatientProfileBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class ConsultationBase(BaseModel):
    chief_complaint: str
    symptoms: Optional[str] = None

class ConsultationCreate(ConsultationBase):
    pass

class ConsultationResponse(ConsultationBase):
    id: int
    patient_id: int
    provider_id: Optional[int] = None
    triage_level: Optional[TriageLevel] = None
    triage_score: Optional[float] = None
    ai_assessment: Optional[str] = None
    differential_diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MedicalImageBase(BaseModel):
    image_type: ImageType

class MedicalImageCreate(MedicalImageBase):
    pass

class MedicalImageResponse(MedicalImageBase):
    id: int
    patient_id: int
    consultation_id: Optional[int] = None
    filename: str
    original_filename: str
    ai_analysis: Optional[str] = None
    confidence_score: Optional[float] = None
    requires_review: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TriageRequest(BaseModel):
    consultation_id: int
    symptoms: List[str]
    medical_history: Optional[List[str]] = None
    vital_signs: Optional[dict] = None

class TriageResponse(BaseModel):
    consultation_id: int
    triage_level: TriageLevel
    triage_score: float
    assessment: dict
    recommendations: List[str]
    confidence: float

class ImageAnalysisRequest(BaseModel):
    image_id: int
    image_type: ImageType

class ImageAnalysisResponse(BaseModel):
    image_id: int
    analysis: dict
    confidence_score: float
    findings: List[str]
    recommendations: List[str]
    requires_review: bool 