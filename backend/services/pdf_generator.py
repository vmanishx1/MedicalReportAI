import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from utils.config import config
from utils.logger import log


class MedicalPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            name="ReportTitle",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=6,
            textColor=colors.HexColor("#0F766E"),
        ))
        self.styles.add(ParagraphStyle(
            name="HospitalName",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=4,
            textColor=colors.HexColor("#14B8A6"),
        ))
        self.styles.add(ParagraphStyle(
            name="SectionHeader",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=18,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor("#0F766E"),
            borderWidth=1,
            borderColor=colors.HexColor("#14B8A6"),
            borderPadding=4,
        ))
        self.styles.add(ParagraphStyle(
            name="NormalText",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
        ))
        self.styles.add(ParagraphStyle(
            name="BoldText",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            name="FooterStyle",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.gray,
        ))

    def generate_report(
        self,
        prediction,
        patient,
        doctor_notes: str = "",
        include_gradcam: bool = True,
    ) -> Path:
        report_dir = config.REPORT_DIR
        report_dir.mkdir(parents=True, exist_ok=True)

        filename = f"medical_report_{prediction.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = report_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.6 * inch,
            rightMargin=0.6 * inch,
        )

        elements = []

        self._add_header(elements)
        self._add_patient_info(elements, patient, prediction)
        self._add_scan_info(elements, prediction)
        self._add_findings(elements, prediction)
        self._add_xray_image(elements, prediction)
        if include_gradcam and prediction.grad_cam_path and os.path.exists(prediction.grad_cam_path):
            self._add_gradcam_image(elements, prediction)
        self._add_clinical_impression(elements, prediction)
        self._add_recommendations(elements, prediction)
        if doctor_notes:
            self._add_doctor_notes(elements, doctor_notes)
        self._add_signature(elements)
        self._add_footer(elements)

        doc.build(elements)
        log.info(f"PDF report generated: {filepath}")
        return filepath

    def _add_header(self, elements):
        elements.append(Paragraph("🏥 MEDICAL REPORT AI", self.styles["ReportTitle"]))
        elements.append(Paragraph("AI-Powered Chest X-Ray Analysis System", self.styles["HospitalName"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles["NormalText"]
        ))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "-" * 80,
            ParagraphStyle("line", fontSize=6, textColor=colors.HexColor("#14B8A6"))
        ))
        elements.append(Spacer(1, 6))

    def _add_patient_info(self, elements, patient, prediction):
        elements.append(Paragraph("PATIENT INFORMATION", self.styles["SectionHeader"]))
        data = [
            ["Patient ID", patient.patient_id or "N/A", "Patient Name", patient.name or "N/A"],
            ["Age", str(patient.age) if patient.age else "N/A", "Gender", patient.gender or "N/A"],
            ["Scan Date", prediction.created_at.strftime("%Y-%m-%d") if prediction.created_at else "N/A", "Report ID", f"RPT-{prediction.id:06d}"],
        ]
        table = Table(data, colWidths=[80, 130, 80, 130])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0FDFA")),
            ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F0FDFA")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 10))

    def _add_scan_info(self, elements, prediction):
        elements.append(Paragraph("SCAN INFORMATION", self.styles["SectionHeader"]))
        data = [
            ["Model Used", prediction.model_used or "DenseNet121"],
            ["Severity", prediction.severity or "N/A"],
            ["Inference Time", f"{prediction.inference_time:.3f}s" if prediction.inference_time else "N/A"],
        ]
        table = Table(data, colWidths=[120, 300])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0FDFA")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 10))

    def _add_findings(self, elements, prediction):
        elements.append(Paragraph("RADIOLOGICAL FINDINGS", self.styles["SectionHeader"]))
        if isinstance(prediction.predictions, dict):
            diseases = prediction.predictions.get("detected_diseases", [])
            if diseases:
                findings_text = []
                for disease in diseases:
                    conf = prediction.confidence_scores.get(disease, 0) if prediction.confidence_scores else 0
                    findings_text.append(f"• {disease}: {conf*100:.1f}% confidence")
                elements.append(Paragraph("<br/>".join(findings_text), self.styles["NormalText"]))
            else:
                elements.append(Paragraph("No significant abnormalities detected.", self.styles["NormalText"]))
        else:
            elements.append(Paragraph(str(prediction.predictions), self.styles["NormalText"]))
        elements.append(Spacer(1, 10))

    def _add_xray_image(self, elements, prediction):
        if prediction.image_path and os.path.exists(prediction.image_path):
            elements.append(Paragraph("CHEST X-RAY IMAGE", self.styles["SectionHeader"]))
            try:
                img = RLImage(prediction.image_path, width=4*inch, height=4*inch)
                elements.append(img)
                elements.append(Spacer(1, 10))
            except Exception as e:
                log.warning(f"Could not add X-ray image to PDF: {e}")

    def _add_gradcam_image(self, elements, prediction):
        if prediction.grad_cam_path and os.path.exists(prediction.grad_cam_path):
            elements.append(Paragraph("AI ACTIVATION MAP (Grad-CAM)", self.styles["SectionHeader"]))
            try:
                img = RLImage(prediction.grad_cam_path, width=4*inch, height=4*inch)
                elements.append(img)
                elements.append(Paragraph(
                    "Heatmap shows regions that contributed most to the AI prediction.",
                    self.styles["NormalText"]
                ))
                elements.append(Spacer(1, 10))
            except Exception as e:
                log.warning(f"Could not add Grad-CAM to PDF: {e}")

    def _add_clinical_impression(self, elements, prediction):
        elements.append(Paragraph("CLINICAL IMPRESSION", self.styles["SectionHeader"]))
        impression = prediction.clinical_impression or "No clinical impression recorded."
        elements.append(Paragraph(impression, self.styles["NormalText"]))
        elements.append(Spacer(1, 10))

    def _add_recommendations(self, elements, prediction):
        elements.append(Paragraph("RECOMMENDATIONS", self.styles["SectionHeader"]))
        recs = prediction.recommendations or "No recommendations recorded."
        elements.append(Paragraph(recs, self.styles["NormalText"]))
        elements.append(Spacer(1, 10))

    def _add_doctor_notes(self, elements, doctor_notes):
        elements.append(Paragraph("DOCTOR'S NOTES", self.styles["SectionHeader"]))
        elements.append(Paragraph(doctor_notes, self.styles["NormalText"]))
        elements.append(Spacer(1, 10))

    def _add_signature(self, elements):
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("-" * 40, self.styles["NormalText"]))
        elements.append(Paragraph("Attending Physician Signature", self.styles["BoldText"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("__________________________", self.styles["NormalText"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("[Hospital Stamp / QR Code Placeholder]", self.styles["NormalText"]))

    def _add_footer(self, elements):
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(
            "This report was generated by Medical Report AI - An AI-assisted diagnostic system.<br/>"
            "All findings should be reviewed and confirmed by a qualified physician.",
            self.styles["FooterStyle"]
        ))
        elements.append(Paragraph(
            f"Page 1 | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Medical Report AI v2.0",
            self.styles["FooterStyle"]
        ))
