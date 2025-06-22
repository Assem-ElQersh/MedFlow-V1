from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import Optional
import httpx
import os
import uuid
from minio import Minio
from minio.error import S3Error
import aiofiles

app = FastAPI(title="MedFlow Imaging Service", version="1.0.0")

# Configuration
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")
MINIO_URL = os.getenv("MINIO_URL", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
BUCKET_NAME = "medical-images"

# Initialize MinIO client
minio_client = Minio(
    MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

class ImageUploadResponse(BaseModel):
    image_id: str
    filename: str
    image_type: str
    upload_url: str
    analysis_status: str

class ImageAnalysisResponse(BaseModel):
    image_id: str
    analysis: dict
    confidence_score: float
    findings: list
    recommendations: list
    requires_review: bool

@app.on_event("startup")
async def startup_event():
    """Create bucket if it doesn't exist"""
    try:
        if not minio_client.bucket_exists(BUCKET_NAME):
            minio_client.make_bucket(BUCKET_NAME)
    except S3Error as e:
        print(f"Error creating bucket: {e}")

@app.get("/")
async def root():
    return {"message": "MedFlow Imaging Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "imaging-service"}

@app.post("/images/upload", response_model=ImageUploadResponse)
async def upload_image(
    image: UploadFile = File(...),
    image_type: str = Form(...),
    consultation_id: Optional[int] = Form(None),
    user_id: int = Form(...)
):
    """
    Upload medical image and trigger AI analysis
    """
    try:
        # Generate unique filename
        image_id = str(uuid.uuid4())
        file_extension = os.path.splitext(image.filename)[1]
        filename = f"{image_id}{file_extension}"
        object_name = f"{image_type}/{filename}"
        
        # Upload to MinIO
        # Read file content
        file_content = await image.read()
        
        # Upload to MinIO
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            data=file_content,
            length=len(file_content),
            content_type=image.content_type
        )
        
        # Generate upload URL for client
        upload_url = f"http://{MINIO_URL}/{BUCKET_NAME}/{object_name}"
        
        # Trigger AI analysis asynchronously
        analysis_status = "pending"
        try:
            async with httpx.AsyncClient() as client:
                ai_request = {
                    "image_path": object_name,
                    "image_type": image_type
                }
                
                # Don't wait for AI analysis to complete
                response = await client.post(
                    f"{AI_SERVICE_URL}/ai/analyze-image",
                    json=ai_request,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    analysis_status = "completed"
                else:
                    analysis_status = "failed"
                    
        except Exception as e:
            print(f"AI analysis trigger failed: {e}")
            analysis_status = "failed"
        
        return ImageUploadResponse(
            image_id=image_id,
            filename=image.filename,
            image_type=image_type,
            upload_url=upload_url,
            analysis_status=analysis_status
        )
        
    except S3Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image upload failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload processing failed: {str(e)}"
        )

@app.get("/images/{image_id}/analysis", response_model=ImageAnalysisResponse)
async def get_image_analysis(image_id: str):
    """
    Get AI analysis results for an image
    """
    try:
        # In a real implementation, this would fetch from database
        # For now, call AI service with mock data
        async with httpx.AsyncClient() as client:
            ai_request = {
                "image_path": f"images/{image_id}.jpg",
                "image_type": "xray"  # Mock type
            }
            
            response = await client.post(
                f"{AI_SERVICE_URL}/ai/analyze-image",
                json=ai_request,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail="AI analysis service unavailable"
                )
            
            ai_result = response.json()
            
            return ImageAnalysisResponse(
                image_id=image_id,
                analysis=ai_result["analysis"],
                confidence_score=ai_result["confidence_score"],
                findings=ai_result["findings"],
                recommendations=ai_result["recommendations"],
                requires_review=ai_result["requires_review"]
            )
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="AI analysis timeout"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis retrieval failed: {str(e)}"
        )

@app.get("/images/{image_id}/download")
async def download_image(image_id: str):
    """
    Download medical image (with proper authentication in production)
    """
    try:
        # Generate presigned URL for download
        url = minio_client.presigned_get_object(
            BUCKET_NAME,
            f"images/{image_id}.jpg",
            expires=timedelta(hours=1)
        )
        return {"download_url": url}
        
    except S3Error as e:
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )

@app.get("/images/stats")
async def get_imaging_stats():
    """
    Get imaging statistics (mock implementation)
    """
    return {
        "total_images": 1247,
        "images_today": 89,
        "pending_review": 12,
        "ai_analysis_accuracy": 0.91,
        "average_processing_time": "2.3 seconds",
        "storage_used": "15.6 GB",
        "image_types": {
            "xray": 645,
            "ct": 234,
            "mri": 156,
            "skin": 212
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 