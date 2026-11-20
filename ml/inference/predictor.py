import os
import cv2
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from utils.config import config
from utils.logger import log
from ml.models.chest_xray_models import (
    get_model, DISEASE_CLASSES, get_model_info
)
from ml.explainability.gradcam import GradCAMExplainer


class ChestXRayPredictor:
    def __init__(self, model_name: str = "best"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = model_name
        self.model = self._load_model()
        self.model.eval()
        self.input_size = 224
        self.explainer = GradCAMExplainer(self.model, self.device)

        self.severity_map = {
            "Pneumonia": {"high": ["Pneumonia", "COVID-19"], "medium": ["TB"]},
            "Cardiomegaly": {"high": ["Cardiomegaly", "Effusion"]},
        }

        self.clinical_impressions = {
            "Pneumonia": "Findings consistent with pneumonic consolidation.",
            "COVID-19": "Features suggestive of COVID-19 pneumonia.",
            "Tuberculosis": "Radiological features suggestive of pulmonary tuberculosis.",
            "Pleural Effusion": "Presence of pleural effusion noted.",
            "Cardiomegaly": "Cardiothoracic ratio is increased, suggesting cardiomegaly.",
            "Edema": "Findings consistent with pulmonary edema.",
            "Atelectasis": "Evidence of atelectasis observed.",
            "Consolidation": "Airspace consolidation detected.",
            "Mass": "Pulmonary mass identified. Further evaluation recommended.",
            "Nodule": "Pulmonary nodule detected. Follow-up recommended.",
            "Fibrosis": "Interstitial fibrotic changes noted.",
            "Normal": "No significant abnormal findings. Lungs are clear.",
        }

        self.recommendations_map = {
            "Pneumonia": "Recommended: Antibiotic therapy, follow-up X-ray in 2 weeks.",
            "COVID-19": "Recommended: RT-PCR confirmation, isolation, symptomatic management.",
            "Tuberculosis": "Recommended: Sputum AFB, GeneXpert, anti-TB therapy.",
            "Pleural Effusion": "Recommended: Thoracentesis, ultrasound evaluation.",
            "Cardiomegaly": "Recommended: Echocardiogram, cardiology consultation.",
            "Edema": "Recommended: Diuretic therapy, cardiac evaluation.",
            "Atelectasis": "Recommended: Chest physiotherapy, deep breathing exercises.",
            "Mass": "Recommended: CT chest, biopsy, oncology consultation.",
            "Normal": "No specific follow-up required. Routine monitoring.",
        }

    def _load_model(self):
        model_path = config.MODEL_PATH
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=self.device)
            model_name = checkpoint.get("model_name", "densenet121")
            num_classes = checkpoint.get("num_classes", len(DISEASE_CLASSES))
            model = get_model(model_name, num_classes=num_classes, pretrained=False)
            model.load_state_dict(checkpoint["model_state_dict"])
            log.info(f"Loaded model from {model_path}")
            return model.to(self.device)
        else:
            log.warning(f"No saved model found at {model_path}. Using pretrained DenseNet121.")
            model = get_model("densenet121", pretrained=True)
            return model.to(self.device)

    def preprocess_image(self, image_path: str) -> Tuple[torch.Tensor, np.ndarray]:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original = image.copy()
        image = cv2.resize(image, (self.input_size, self.input_size))
        image = image.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image = (image - mean) / std
        image = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).float()
        return image.to(self.device), original

    def predict(self, image_path: str) -> Dict:
        try:
            input_tensor, original_image = self.preprocess_image(image_path)

            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.sigmoid(outputs).cpu().numpy()[0]

            detected = {}
            for i, disease in enumerate(DISEASE_CLASSES):
                if probabilities[i] > 0.3:
                    detected[disease] = float(probabilities[i])

            if "Normal" in detected and len(detected) == 1:
                is_healthy = True
                detected.pop("Normal")
            else:
                is_healthy = False
                detected.pop("Normal", None)

            if not detected:
                is_healthy = True
                detected = {"Normal": float(probabilities[DISEASE_CLASSES.index("Normal")])}

            grad_cam_path = self.explainer.generate_gradcam(
                input_tensor, original_image, image_path, detected
            )

            severity = self._determine_severity(detected)
            impression = self._generate_clinical_impression(detected)
            recommendations = self._generate_recommendations(detected)

            return {
                "predictions": {"detected_diseases": list(detected.keys()), "all_scores": {d: round(s, 4) for d, s in detected.items()}},
                "confidence_scores": {d: round(s, 4) for d, s in detected.items()},
                "severity": severity,
                "model_used": "DenseNet121 (Ensemble)",
                "is_healthy": is_healthy,
                "clinical_impression": impression,
                "recommendations": recommendations,
                "grad_cam_path": grad_cam_path,
            }

        except Exception as e:
            log.error(f"Prediction error: {e}")
            return {
                "predictions": {"detected_diseases": ["Error"], "all_scores": {}},
                "confidence_scores": {},
                "severity": "Unknown",
                "model_used": "N/A",
                "is_healthy": False,
                "clinical_impression": "Error during analysis.",
                "recommendations": "Please re-upload the image.",
                "grad_cam_path": "",
            }

    def _determine_severity(self, detected: Dict) -> str:
        max_conf = max(detected.values()) if detected else 0
        if max_conf >= 0.8:
            return "Severe"
        elif max_conf >= 0.5:
            return "Moderate"
        return "Mild"

    def _generate_clinical_impression(self, detected: Dict) -> str:
        impressions = []
        for disease in detected:
            if disease in self.clinical_impressions:
                impressions.append(self.clinical_impressions[disease])

        if not impressions:
            return "No significant findings detected."

        impression_text = " ".join(impressions)
        if any(c in detected for c in ["Mass", "Nodule"]):
            impression_text += " Further clinical correlation and follow-up imaging recommended."
        return impression_text

    def _generate_recommendations(self, detected: Dict) -> str:
        recs = []
        for disease in detected:
            if disease in self.recommendations_map:
                recs.append(self.recommendations_map[disease])
        if not recs:
            recs.append(self.recommendations_map.get("Normal", "Routine follow-up."))
        return " ".join(recs)
