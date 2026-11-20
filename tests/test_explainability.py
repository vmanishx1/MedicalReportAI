import pytest
import torch
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.explainability.gradcam import GradCAMExplainer
from ml.models.chest_xray_models import get_model


class TestGradCAM:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.device = torch.device("cpu")
        self.model = get_model("densenet121", pretrained=False).to(self.device)
        self.model.eval()
        self.explainer = GradCAMExplainer(self.model, self.device)

    def test_heatmap_generation(self):
        input_tensor = torch.randn(1, 3, 224, 224)
        cam = self.explainer.generate_heatmap(input_tensor, target_class=0)
        assert cam.shape == (224, 224)
        assert cam.min() >= 0
        assert cam.max() <= 1.0

    def test_overlay_heatmap(self):
        image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        cam = np.random.rand(224, 224)
        overlay = self.explainer._overlay_heatmap(image, cam)
        assert overlay.shape == (224, 224, 3)

    def test_explanation_text(self):
        detected = {"Pneumonia": 0.85, "Cardiomegaly": 0.65}
        text = self.explainer.get_explanation_text(detected)
        assert "Pneumonia" in text
        assert "Cardiomegaly" in text
        assert "lower lung" in text
