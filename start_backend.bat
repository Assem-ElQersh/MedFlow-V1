@echo off
echo Starting MedFlow Backend Services...

:: Load environment variables from .env file
call load_env.bat
if errorlevel 1 (
    echo Using fallback environment variables...
    set DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/medflow
    set REDIS_URL=redis://localhost:6379
    set MINIO_URL=localhost:9000
    set MINIO_ACCESS_KEY=minioadmin
    set MINIO_SECRET_KEY=minioadmin123
)

:: Activate conda environment
call conda activate medflow

echo Environment configured successfully!
echo Database: %DATABASE_URL%
echo Starting API Gateway on port 8000...

:: Start API Gateway
cd backend\api-gateway
start "API Gateway" uvicorn main:app --host 0.0.0.0 --port 8000 --reload

:: Wait a moment then start other services
timeout /t 3 /nobreak >nul

cd ..\ai-service
start "AI Service" uvicorn main:app --host 0.0.0.0 --port 8005 --reload

cd ..\patient-service  
start "Patient Service" uvicorn main:app --host 0.0.0.0 --port 8001 --reload

cd ..\triage-service
start "Triage Service" uvicorn main:app --host 0.0.0.0 --port 8002 --reload

cd ..\imaging-service
start "Imaging Service" uvicorn main:app --host 0.0.0.0 --port 8003 --reload

cd ..\clinical-service
start "Clinical Service" uvicorn main:app --host 0.0.0.0 --port 8004 --reload

cd ..\..

echo All backend services started!
echo Frontend: http://localhost:3000
echo API Gateway: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
pause 