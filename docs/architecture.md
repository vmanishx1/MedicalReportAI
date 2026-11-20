# Architecture Document

## System Architecture

The Medical Report AI system follows a microservices-based architecture with three main components:

## 1. Frontend Layer (Streamlit)
- **User Interface**: Professional hospital dashboard
- **Authentication**: JWT-based login/signup
- **Visualization**: Interactive charts using Plotly
- **Pages**: Dashboard, Upload, Predictions, Reports, History, Analytics, Settings

## 2. Backend Layer (FastAPI)
- **API Gateway**: RESTful endpoints for all operations
- **Authentication Service**: JWT token generation, bcrypt password hashing
- **Prediction Service**: Image analysis pipeline
- **Report Service**: PDF generation using ReportLab
- **Analytics Service**: Data aggregation and statistics

## 3. ML Layer (PyTorch)
- **Model Zoo**: EfficientNet-B3, ResNet50, DenseNet121, ViT
- **Preprocessing Pipeline**: Noise removal, contrast enhancement, augmentation
- **Inference Engine**: Model loading, prediction, post-processing
- **Explainability Module**: Grad-CAM heatmap generation
- **Evaluation**: Metrics computation, visualization

## Data Flow

1. User uploads chest X-ray image via Streamlit UI
2. Image sent to FastAPI backend
3. Backend preprocesses image and runs ML inference
4. Model predicts diseases with confidence scores
5. Grad-CAM generates attention heatmap
6. Results returned to frontend for display
7. User can generate PDF report
8. All data persisted to SQLite database

## Database Schema

### Users Table
- id, username, email, hashed_password, full_name, role, is_active, timestamps

### Patients Table
- id, patient_id, name, age, gender, contact, address, medical_history

### Predictions Table
- id, user_id, patient_id, image_path, predictions (JSON), confidence_scores (JSON), severity, model_used, inference_time, grad_cam_path, is_healthy, clinical_impression, recommendations

### Reports Table
- id, prediction_id, report_path, findings, impression, recommendations, doctor_notes

### LoginLogs Table
- id, user_id, ip_address, user_agent, login_time, success

## Security Architecture

- JWT tokens with configurable expiry
- bcrypt password hashing
- File validation (type, size, content)
- SQL injection prevention via SQLAlchemy ORM
- CORS middleware for frontend-backend communication
