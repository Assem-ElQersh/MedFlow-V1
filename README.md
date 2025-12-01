# MedFlow-V1 - Advanced Medical Assistance System

AI-Powered Healthcare Platform with Google MedGemma Integration

MedFlow-V1 is a cutting-edge medical assistance system that leverages Google's MedGemma 4B IT, the latest medical AI model from Google DeepMind. This platform provides real-time medical image analysis, patient triage, and clinical decision support.

## Overview

MedFlow-V1 is designed as a comprehensive AI-powered healthcare platform that integrates advanced medical image analysis with intelligent patient management. The system uses Google's MedGemma 4B IT model to provide clinical-grade findings and recommendations for various medical imaging modalities.

## Key Features

- **Real AI Medical Analysis**: Google MedGemma 4B IT integration via live Gradio demo
- **Real-time Medical Image Interpretation**: Support for X-Ray, CT, MRI, and Dermatology images
- **Clinical-grade Findings**: Professional medical findings and recommendations
- **Hospital Management**: Patient registration and consultation tracking
- **Intelligent Triage System**: Priority scoring based on AI analysis
- **Real-time Dashboard**: System status monitoring and analytics
- **Medical Image Upload**: Workflow for medical image analysis
- **Service Status Monitoring**: Track all system components
- **Patient Queue Management**: Organize and prioritize consultations
- **Consultation Statistics**: Insights and performance tracking
- **AI Model Performance Tracking**: Monitor MedGemma accuracy and response times

## Technology Stack

**Backend:**
- FastAPI (Python async web framework)
- SQLAlchemy (ORM with PostgreSQL)
- Redis (Session management and caching)
- Celery (Background task processing)
- Python-Jose (JWT authentication)
- Passlib with bcrypt (Password hashing)
- Google Cloud Storage (File storage via MinIO)
- Gradio Client (MedGemma integration)

**Frontend:**
- React 18
- React Router v6
- Axios (HTTP client)
- Modern CSS with responsive design

**AI/ML:**
- Google MedGemma 4B IT (via Gradio demo)
- Hugging Face Inference API (optional)
- Local model support (GPU required)

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL (Database)
- Redis (Cache)
- MinIO (Object storage)

## System Architecture

The system follows a microservices architecture with the following components:

```
Frontend (React) 
    ↓
API Gateway (FastAPI)
    ↓
├── Patient Service (Port 8001)
├── Triage Service (Port 8002)
├── Imaging Service (Port 8003)
├── Clinical Service (Port 8004)
└── AI Service (Port 8005)
    ↓
MedGemma Integration
    ├── Live Gradio Demo
    ├── HuggingFace API
    └── Local Model
```

### Component Details

- **Frontend**: React.js with modern UI/UX on port 3000
- **API Gateway**: Main entry point on port 8000 with FastAPI
- **Patient Service**: Patient management and records
- **Triage Service**: AI-powered triage analysis
- **Imaging Service**: Medical image upload and processing
- **Clinical Service**: Clinical workflows and differential diagnosis
- **AI Service**: MedGemma integration and analysis
- **Database**: PostgreSQL for data persistence
- **Cache**: Redis for session management
- **Storage**: MinIO for medical images

## MedGemma AI Integration

### Architecture

MedFlow-V1 integrates with Google's MedGemma 4B IT through multiple pathways:

1. **Live Demo Mode** (Default): Direct connection to Hugging Face Gradio demo
2. **API Mode**: Hugging Face Inference API (requires token)
3. **Local Mode**: Download and run MedGemma locally (requires GPU)

### Model Specifications

- **Model**: Google MedGemma 4B IT (Instruction Tuned)
- **Parameters**: 4 billion (multimodal)
- **Architecture**: Gemma 3 with medical fine-tuning
- **Training Data**: De-identified medical images and text
- **Modalities**: Text + Vision (medical images)
- **Release**: May 2025 by Google DeepMind
- **Accuracy**: Clinical-grade performance on medical benchmarks

### Supported Image Types

- **Chest X-Ray**: Cardiopulmonary assessment
- **CT Scan**: Intracranial and body imaging
- **MRI**: Magnetic resonance analysis
- **Dermatology**: Skin lesion evaluation
- **Fundus**: Ophthalmological assessment

### Clinical Applications

- Medical image classification and interpretation
- Clinical text analysis and summarization
- Patient interview assistance and triage
- Differential diagnosis support
- Treatment recommendation guidance

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    role VARCHAR CHECK (role IN ('patient', 'physician', 'nurse', 'specialist', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Patients Table

```sql
CREATE TABLE patient_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date_of_birth DATE,
    gender VARCHAR(10),
    phone VARCHAR(20),
    address TEXT,
    emergency_contact TEXT,
    medical_history TEXT,
    allergies TEXT,
    medications TEXT
);
```

### Consultations Table

```sql
CREATE TABLE consultations (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patient_profiles(id),
    provider_id INTEGER REFERENCES provider_profiles(id),
    chief_complaint TEXT,
    symptoms TEXT,
    triage_level VARCHAR CHECK (triage_level IN ('critical', 'urgent', 'routine')),
    triage_score FLOAT,
    ai_assessment TEXT,
    differential_diagnosis TEXT,
    treatment_plan TEXT,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Medical Images Table

```sql
CREATE TABLE medical_images (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patient_profiles(id),
    consultation_id INTEGER REFERENCES consultations(id),
    filename VARCHAR(255),
    file_path VARCHAR(500),
    image_type VARCHAR CHECK (image_type IN ('xray', 'ct', 'mri', 'skin', 'fundus')),
    ai_analysis TEXT,
    confidence_score FLOAT,
    requires_review BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 16+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/medflow-v1.git
cd medflow-v1
```

2. Start services with Docker Compose:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Default Credentials

After initialization, use these credentials:

- **Patient**: username: `patient@demo.com`, password: `password123`
- **Doctor**: username: `doctor@demo.com`, password: `password123`

## Manual Setup (Development)

### Backend

```bash
# Create conda environment
conda create -n medflow python=3.11 -y
conda activate medflow

# Install dependencies
pip install -r requirements.txt
pip install gradio_client

# Start API server
python demo_api.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Configuration Options

### Environment Variables

```bash
# Database configuration
DATABASE_URL=postgresql://user:pass@localhost/medflow
REDIS_URL=redis://localhost:6379

# MedGemma configuration (optional)
HUGGINGFACE_TOKEN=hf_your_token_here

# Storage configuration
MINIO_URL=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
```

### Docker Infrastructure

```bash
# Start supporting services
docker-compose up -d

# Services included:
# - PostgreSQL (port 5432)
# - Redis (port 6379)
# - MinIO (ports 9000-9001)
```

## Advanced MedGemma Setup

### Real MedGemma API Integration

For production use with enhanced capabilities:

1. Get HuggingFace Token: https://huggingface.co/settings/tokens
2. Create account (free)
3. Generate new token with "Read" access
4. Set environment variable:
```bash
export HUGGINGFACE_TOKEN=hf_your_token_here
```
5. Restart API: The system will automatically use enhanced API access

### Local MedGemma Model

For offline or private deployments:

```bash
# Install model dependencies
pip install transformers torch torchvision

# Download MedGemma 4B model (requires 16GB+ storage)
python -c "
from huggingface_hub import snapshot_download
snapshot_download('google/medgemma-4b-it', local_dir='./models/medgemma')
"
```

## Project Structure

```
MedFlow-V1/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── backend/
│   ├── ai-service/
│   │   ├── main.py
│   │   └── Dockerfile
│   ├── api-gateway/
│   │   ├── main.py
│   │   └── Dockerfile
│   ├── clinical-service/
│   ├── imaging-service/
│   ├── patient-service/
│   ├── triage-service/
│   └── shared/
│       ├── database.py
│       ├── models.py
│       └── auth.py
├── demo_api.py
├── gradio_medgemma_service.py
├── medgemma_service.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## System Workflow

### Patient Workflow

1. Login to system
2. Create new consultation
3. Enter symptoms and medical history
4. Upload medical images (optional)
5. Submit for AI triage
6. Receive AI assessment
7. Wait for doctor review

### AI Processing (Automatic)

1. Consultation submitted by patient
2. MedGemma analyzes patient context, symptoms, and images
3. Generates medical findings and observations
4. Calculates triage score and priority
5. Routes to appropriate doctor queue

### Physician Workflow

1. View consultation queue
2. Review AI findings and recommendations
3. Examine uploaded medical images
4. Provide diagnosis
5. Prescribe treatment
6. Complete consultation

## API Documentation

Once running, access interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Performance Metrics

- **API Response Time**: Less than 200ms for local operations
- **MedGemma Analysis**: 2-10 seconds depending on image complexity
- **Concurrent Users**: 50+ with proper infrastructure
- **Image Processing**: Supports up to 10MB medical images
- **Supported Formats**: JPEG, PNG, DICOM

## Security and Compliance

- **Authentication**: Token-based JWT authentication system
- **Data Privacy**: No medical data stored permanently in demo mode
- **CORS**: Configured for secure cross-origin requests
- **Input Validation**: Comprehensive request validation
- **Medical Disclaimer**: Built-in disclaimers for AI analysis
- **HTTPS**: SSL/TLS support for production

## Production Deployment

### Security Checklist

- Change SECRET_KEY in environment variables
- Set DEBUG=False
- Configure proper CORS origins
- Use strong passwords for all default users
- Set up SSL/TLS certificates
- Configure database authentication
- Set up Redis password
- Configure Google Cloud Storage credentials
- Implement backup strategy
- Enable logging and monitoring

### Deployment Options

#### Development

```bash
conda activate medflow
python demo_api.py  # Backend on :8000
npm start           # Frontend on :3000
```

#### Production

```bash
# Docker deployment
docker-compose up -d

# Or manual deployment
gunicorn demo_api:app --host 0.0.0.0 --port 8000
serve -s frontend/build -l 3000
```

## Roadmap

- Enhanced AI Models: Integration with additional medical AI models
- FHIR Compliance: HL7 FHIR standard support
- Mobile App: React Native mobile application
- Multi-language: International language support
- Advanced Analytics: ML-powered insights dashboard
- Telemedicine: Video consultation integration
- Electronic Health Records: Full EHR system integration
- Laboratory Integration: Direct lab result imports
- Pharmacy Integration: E-prescribing capabilities

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Medical Disclaimer

This system is designed for educational and demonstration purposes. MedGemma AI analysis should not replace professional medical judgment. All AI-generated findings and recommendations must be reviewed and validated by licensed healthcare professionals before clinical use.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
