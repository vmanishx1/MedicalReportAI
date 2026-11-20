# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

### Register
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "doctor",
    "email": "doctor@hospital.com",
    "password": "securepass",
    "full_name": "Dr. John Doe"
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "doctor",
    "password": "securepass"
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

## Predictions

### Upload & Predict
```http
POST /api/predictions/upload-predict
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <xray_image>
patient_name: "John Doe"
patient_age: 45
patient_gender: "Male"
```

### Get History
```http
GET /api/predictions/history?skip=0&limit=20
Authorization: Bearer <token>
```

### Search
```http
GET /api/predictions/search?query=pneumonia
Authorization: Bearer <token>
```

### Delete
```http
DELETE /api/predictions/{prediction_id}
Authorization: Bearer <token>
```

## Analytics

### Dashboard Stats
```http
GET /api/analytics/dashboard
Authorization: Bearer <token>
```

### Disease Distribution
```http
GET /api/analytics/disease-distribution
Authorization: Bearer <token>
```

### Monthly Cases
```http
GET /api/analytics/monthly-cases?months=6
Authorization: Bearer <token>
```

### Gender Analysis
```http
GET /api/analytics/gender-analysis
Authorization: Bearer <token>
```

### Age Distribution
```http
GET /api/analytics/age-distribution
Authorization: Bearer <token>
```

## Reports

### Generate Report
```http
POST /api/reports/generate
Authorization: Bearer <token>
Content-Type: application/json

{
    "prediction_id": 1,
    "doctor_notes": "Patient shows improvement",
    "include_gradcam": true
}
```

### Download Report
```http
GET /api/reports/download/{report_id}
Authorization: Bearer <token>
```

## Health Check
```http
GET /health
```
