import time
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.database.database import get_db
from backend.database.models import User, Patient, Prediction, Report
from backend.auth.auth_handler import get_current_user
from utils.config import config
from utils.helpers import generate_patient_id, generate_uuid, validate_image_extension
from utils.logger import log

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


class PredictionResponse(BaseModel):
    id: int
    patient_id: str
    patient_name: str
    predictions: dict
    confidence_scores: dict
    severity: str
    model_used: str
    inference_time: float
    is_healthy: bool
    clinical_impression: str
    recommendations: str
    image_path: str
    grad_cam_path: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class PatientRequest(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None


@router.post("/upload-predict")
async def upload_and_predict(
    request: Request,
    file: UploadFile = File(...),
    patient_name: str = Form("Unknown"),
    patient_age: Optional[int] = Form(None),
    patient_gender: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not validate_image_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PNG, JPEG, JPG allowed."
        )

    content = await file.read()
    if len(content) > config.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum 20 MB allowed."
        )

    from utils.helpers import hash_image
    file_hash = hash_image(content)
    ext = file.filename.rsplit(".", 1)[-1].lower()
    save_name = f"{file_hash}_{int(time.time())}.{ext}"
    save_path = config.UPLOAD_DIR / save_name
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path.write_bytes(content)

    patient = db.query(Patient).filter(
        Patient.name == patient_name
    ).first()
    if not patient:
        patient = Patient(
            patient_id=generate_patient_id(),
            name=patient_name,
            age=patient_age,
            gender=patient_gender,
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

    from ml.inference.predictor import ChestXRayPredictor
    predictor = ChestXRayPredictor()
    start_time = time.time()
    result = predictor.predict(str(save_path))
    inference_time = time.time() - start_time

    prediction = Prediction(
        user_id=current_user.id,
        patient_id=patient.id,
        image_path=str(save_path),
        original_filename=file.filename,
        predictions=result["predictions"],
        confidence_scores=result["confidence_scores"],
        severity=result["severity"],
        model_used=result["model_used"],
        inference_time=inference_time,
        grad_cam_path=result.get("grad_cam_path", ""),
        is_healthy=result.get("is_healthy", False),
        clinical_impression=result.get("clinical_impression", ""),
        recommendations=result.get("recommendations", ""),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return {
        "prediction_id": prediction.id,
        "patient_id": patient.patient_id,
        "patient_name": patient.name,
        "predictions": result["predictions"],
        "confidence_scores": result["confidence_scores"],
        "severity": result["severity"],
        "model_used": result["model_used"],
        "inference_time": inference_time,
        "is_healthy": result.get("is_healthy", False),
        "clinical_impression": result.get("clinical_impression", ""),
        "recommendations": result.get("recommendations", ""),
        "grad_cam_path": result.get("grad_cam_path", ""),
    }


@router.get("/history", response_model=List[PredictionResponse])
def get_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    predictions = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for p in predictions:
        patient = db.query(Patient).filter(Patient.id == p.patient_id).first()
        result.append(PredictionResponse(
            id=p.id,
            patient_id=patient.patient_id if patient else "",
            patient_name=patient.name if patient else "Unknown",
            predictions=p.predictions,
            confidence_scores=p.confidence_scores,
            severity=p.severity,
            model_used=p.model_used,
            inference_time=p.inference_time,
            is_healthy=p.is_healthy,
            clinical_impression=p.clinical_impression or "",
            recommendations=p.recommendations or "",
            image_path=p.image_path,
            grad_cam_path=p.grad_cam_path,
            created_at=p.created_at.isoformat() if p.created_at else "",
        ))
    return result


@router.get("/search")
def search_predictions(
    query: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    predictions = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )

    results = []
    for p in predictions:
        patient = db.query(Patient).filter(Patient.id == p.patient_id).first()
        if patient and (
            query.lower() in patient.name.lower()
            or query.lower() in patient.patient_id.lower()
            or any(query.lower() in d.lower() for d in p.predictions.get("detected_diseases", []))
        ):
            results.append({
                "id": p.id,
                "patient_id": patient.patient_id,
                "patient_name": patient.name,
                "predictions": p.predictions,
                "created_at": p.created_at.isoformat() if p.created_at else "",
            })
    return results


@router.delete("/{prediction_id}")
def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id,
    ).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    db.delete(prediction)
    db.commit()
    return {"message": "Prediction deleted successfully"}
