# 🏥 Medical Report AI

**AI-Powered Chest X-Ray Analysis & Diagnostic Report Generation System**

A production-grade enterprise medical AI platform that automatically analyzes Chest X-ray images and generates complete medical diagnostic reports using Deep Learning, Computer Vision, NLP, and Explainable AI.

---

## ✨ Features

### 🔬 Deep Learning Models
| Model | Parameters | Input Size | Description |
|-------|-----------|------------|-------------|
| **EfficientNet-B3** | 12M | 300×300 | Efficient learning with compound scaling |
| **ResNet-50** | 25.6M | 224×224 | Residual learning framework |
| **DenseNet-121** | 8M | 224×224 | Dense connectivity pattern |
| **Vision Transformer (ViT)** | 86M | 224×224 | Transformer-based image classification |

Auto-selects best performing model.

### 🏥 Disease Detection (15+ conditions)
- Pneumonia, COVID-19, Tuberculosis
- Pleural Effusion, Cardiomegaly
- Edema, Atelectasis, Consolidation
- Mass, Nodule, Fibrosis, Emphysema
- Infiltration, Hernia, Pleural Thickening
- Multi-label prediction supported

### 📋 Report Generation
- CNN Encoder + Transformer Decoder
- Complete clinical report generation
- Findings, Impression, Recommendations
- Professional PDF with ReportLab

### 🔍 Explainable AI (XAI)
- **Grad-CAM** heatmap visualization
- Highlighted affected regions
- Confidence-based explanations
- Attention maps for interpretability

### 📊 Enterprise Dashboard
- Patient scanning metrics
- Disease distribution analytics
- Gender & age-wise analysis
- Monthly trends & predictions
- Interactive charts (Plotly)

### 🔐 Authentication
- JWT-based authentication
- Password hashing (bcrypt)
- Session management
- Login logging

### 📱 Additional Features
- 📄 Automated PDF report generation
- 📁 Patient history management
- 🔍 Search by name/ID/disease
- 🌙 Dark/Light mode
- 📈 Training dashboard with metrics
- 🏢 PostgreSQL-ready architecture

---

## 🏗️ Architecture

```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Streamlit UI      │────▶│   FastAPI        │────▶│   ML Models     │
│   (Frontend)        │◀────│   (Backend)      │◀────│   (PyTorch)     │
└─────────────────────┘     └──────────────────┘     └─────────────────┘
                                    │                         │
                                    ▼                         ▼
                            ┌──────────────────┐     ┌─────────────────┐
                            │   SQLite/        │     │   Grad-CAM      │
                            │   PostgreSQL     │     │   Explainability│
                            └──────────────────┘     └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PyTorch 2.0+
- 8GB+ RAM (16GB recommended for ViT)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/MedicalReportAI.git
cd MedicalReportAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Run the frontend (in new terminal)
streamlit run app/main.py --server.port 8501
```

### Docker Deployment

```bash
docker-compose up --build
```

Access:
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
MedicalReportAI/
├── app/                    # Streamlit Frontend
│   ├── main.py            # App entry point
│   ├── pages/             # Page components
│   │   ├── auth_page.py
│   │   ├── dashboard.py
│   │   ├── upload.py
│   │   ├── predictions.py
│   │   ├── reports_page.py
│   │   ├── history.py
│   │   ├── analytics.py
│   │   └── settings.py
│   └── components/        # Reusable components
│       ├── sidebar.py
│       └── styles.py
├── backend/               # FastAPI Backend
│   ├── main.py
│   ├── api/               # API routes
│   │   ├── auth_routes.py
│   │   ├── prediction_routes.py
│   │   ├── analytics_routes.py
│   │   └── report_routes.py
│   ├── auth/              # Auth logic
│   │   └── auth_handler.py
│   ├── database/          # Database layer
│   │   ├── database.py
│   │   └── models.py
│   └── services/          # Business logic
│       └── pdf_generator.py
├── ml/                    # Machine Learning
│   ├── models/            # Model architectures
│   │   ├── chest_xray_models.py
│   │   └── report_generator.py
│   ├── preprocessing/     # Data pipeline
│   │   └── dataset.py
│   ├── training/          # Training scripts
│   │   └── trainer.py
│   ├── inference/         # Inference engine
│   │   └── predictor.py
│   ├── explainability/    # XAI modules
│   │   └── gradcam.py
│   └── evaluation/        # Evaluation metrics
│       └── metrics.py
├── utils/                 # Utilities
│   ├── config.py
│   ├── helpers.py
│   └── logger.py
├── tests/                 # Test suite
│   ├── test_api.py
│   ├── test_models.py
│   ├── test_preprocessing.py
│   └── test_explainability.py
├── docs/                  # Documentation
├── datasets/              # Dataset storage
├── saved_models/          # Trained models
├── reports/               # Generated PDFs
├── history/               # Patient history
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🔌 API Documentation

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/logout` | Logout |

### Predictions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predictions/upload-predict` | Upload X-ray & predict |
| GET | `/api/predictions/history` | Get prediction history |
| GET | `/api/predictions/search?query=` | Search predictions |
| DELETE | `/api/predictions/{id}` | Delete prediction |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Dashboard statistics |
| GET | `/api/analytics/disease-distribution` | Disease distribution |
| GET | `/api/analytics/monthly-cases` | Monthly case trends |
| GET | `/api/analytics/gender-analysis` | Gender-wise analysis |
| GET | `/api/analytics/age-distribution` | Age-wise analysis |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reports/generate` | Generate PDF report |
| GET | `/api/reports/download/{id}` | Download PDF |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v --cov=.

# Run specific test files
pytest tests/test_models.py -v
pytest tests/test_api.py -v
pytest tests/test_preprocessing.py -v
```

---

## 🎯 Dataset Preparation

The system is designed for **ChestX-ray14** and **MIMIC-CXR** datasets.

```python
from ml.preprocessing.dataset import Preprocessor, remove_duplicates, compute_dataset_stats

# Preprocess pipeline
preprocessor = Preprocessor()
image = preprocessor.preprocess_pipeline("xray.jpg", input_size=224)

# Remove duplicates
unique_paths = remove_duplicates(all_image_paths)

# Get dataset stats
stats = compute_dataset_stats(unique_paths)
```

---

## 🏋️ Training

```python
from ml.training.trainer import ModelTrainer

trainer = ModelTrainer(model_name="densenet121")
history = trainer.train(train_loader, val_loader, epochs=50)
eval_results = trainer.evaluate(test_loader)
```

### Train all models:
```python
from ml.training.trainer import train_all_models

results, best_model = train_all_models(train_loader, val_loader, test_loader, epochs=30)
print(f"Best model: {best_model}")
```

---

## 🖥️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit, HTML, CSS, JavaScript, Plotly |
| **Backend** | FastAPI, Python, JWT, bcrypt |
| **Database** | SQLite (PostgreSQL-ready) |
| **Deep Learning** | PyTorch, TorchVision, Transformers, HuggingFace |
| **CV** | OpenCV, Albumentations, Scikit-Image |
| **Explainability** | Grad-CAM |
| **PDF** | ReportLab |
| **Deployment** | Docker, Docker Compose |

---

## 🔮 Future Enhancements

- [ ] CT Scan & MRI support
- [ ] DICOM format support
- [ ] Multi-language reports
- [ ] Voice-based report reading
- [ ] Cloud deployment (AWS/GCP/Azure)
- [ ] FHIR & PACS integration
- [ ] Doctor review panel
- [ ] Mobile app
- [ ] Multi-hospital support
- [ ] Real-time streaming inference

---

## 📄 License

MIT License - see LICENSE file for details.

## 👥 Contributors

- Medical AI Research Lab
- Built with ❤️ for healthcare innovation
