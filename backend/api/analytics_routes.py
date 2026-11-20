from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from backend.database.database import get_db
from backend.database.models import Prediction, Patient, User
from backend.auth.auth_handler import get_current_user
from utils.logger import log

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_predictions = db.query(Prediction).count()
    total_patients = db.query(Patient).count()
    healthy = db.query(Prediction).filter(Prediction.is_healthy == True).count()
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_reports = db.query(Prediction).filter(Prediction.created_at >= today_start).count()

    avg_confidence = 0
    if total_predictions > 0:
        scores = db.query(Prediction.confidence_scores).all()
        all_scores = []
        for s in scores:
            if s[0]:
                all_scores.extend(s[0].values())
        avg_confidence = sum(all_scores) / len(all_scores) if all_scores else 0

    model_acc = db.query(Prediction.model_used, func.count(Prediction.id)).group_by(
        Prediction.model_used
    ).all()

    return {
        "total_predictions": total_predictions,
        "total_patients": total_patients,
        "healthy_patients": healthy,
        "average_confidence": round(avg_confidence, 3),
        "today_reports": today_reports,
        "model_accuracy": {m: c for m, c in model_acc},
    }


@router.get("/disease-distribution")
def disease_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    predictions = db.query(Prediction.predictions).all()
    disease_counts = {}
    for p in predictions:
        if p[0] and "detected_diseases" in p[0]:
            for disease in p[0]["detected_diseases"]:
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
    return disease_counts


@router.get("/monthly-cases")
def monthly_cases(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.utcnow() - timedelta(days=months * 30)
    cases = (
        db.query(
            extract("year", Prediction.created_at).label("year"),
            extract("month", Prediction.created_at).label("month"),
            func.count(Prediction.id).label("count"),
        )
        .filter(Prediction.created_at >= since)
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )
    return [
        {"year": int(c.year), "month": int(c.month), "count": c.count}
        for c in cases
    ]


@router.get("/gender-analysis")
def gender_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = {}
    patients = db.query(Patient.gender, Patient.id).all()
    gender_patient_ids = {}
    for gender, pid in patients:
        if gender:
            gender_patient_ids.setdefault(gender, []).append(pid)

    for gender, pids in gender_patient_ids.items():
        count = db.query(Prediction).filter(Prediction.patient_id.in_(pids)).count()
        results[gender] = count
    return results


@router.get("/age-distribution")
def age_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    age_groups = {"0-18": 0, "19-35": 0, "36-50": 0, "51-65": 0, "65+": 0}
    patients = db.query(Patient.age, Patient.id).all()
    for age, pid in patients:
        if age is None:
            continue
        predictions_count = db.query(Prediction).filter(Prediction.patient_id == pid).count()
        if age <= 18:
            age_groups["0-18"] += predictions_count
        elif age <= 35:
            age_groups["19-35"] += predictions_count
        elif age <= 50:
            age_groups["36-50"] += predictions_count
        elif age <= 65:
            age_groups["51-65"] += predictions_count
        else:
            age_groups["65+"] += predictions_count
    return age_groups
