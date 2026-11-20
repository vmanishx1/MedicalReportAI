from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.database.database import get_db
from backend.database.models import User, Prediction, Patient, Report
from backend.auth.auth_handler import get_current_user
from utils.logger import log

router = APIRouter(prefix="/api/reports", tags=["Reports"])


class ReportGenerateRequest(BaseModel):
    prediction_id: int
    doctor_notes: Optional[str] = ""
    include_gradcam: bool = True


@router.post("/generate")
def generate_report(
    req: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from backend.services.pdf_generator import MedicalPDFGenerator

    prediction = db.query(Prediction).filter(Prediction.id == req.prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    patient = db.query(Patient).filter(Patient.id == prediction.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    pdf_gen = MedicalPDFGenerator()
    report_path = pdf_gen.generate_report(
        prediction=prediction,
        patient=patient,
        doctor_notes=req.doctor_notes,
        include_gradcam=req.include_gradcam,
    )

    report = Report(
        prediction_id=prediction.id,
        report_path=str(report_path),
        findings=str(prediction.predictions),
        impression=prediction.clinical_impression,
        recommendations=prediction.recommendations,
        doctor_notes=req.doctor_notes,
    )
    db.add(report)
    db.commit()

    return {"report_path": str(report_path), "message": "Report generated successfully"}


@router.get("/download/{report_id}")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report or not report.report_path:
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        report.report_path,
        media_type="application/pdf",
        filename=f"medical_report_{report_id}.pdf",
    )


@router.get("/{prediction_id}")
def get_reports_for_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = db.query(Report).filter(Report.prediction_id == prediction_id).all()
    return [
        {
            "id": r.id,
            "report_path": r.report_path,
            "findings": r.findings,
            "impression": r.impression,
            "generated_at": r.generated_at.isoformat() if r.generated_at else "",
        }
        for r in reports
    ]
