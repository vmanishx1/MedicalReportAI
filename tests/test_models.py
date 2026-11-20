import pytest
import torch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.models.chest_xray_models import (
    get_model, DISEASE_CLASSES, NUM_CLASSES, get_model_info
)


class TestModels:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.device = torch.device("cpu")
        self.batch_size = 2

    def test_densenet121_creation(self):
        model = get_model("densenet121", pretrained=False)
        assert model is not None
        x = torch.randn(self.batch_size, 3, 224, 224)
        output = model(x)
        assert output.shape == (self.batch_size, NUM_CLASSES)

    def test_resnet50_creation(self):
        model = get_model("resnet50", pretrained=False)
        assert model is not None
        x = torch.randn(self.batch_size, 3, 224, 224)
        output = model(x)
        assert output.shape == (self.batch_size, NUM_CLASSES)

    def test_efficientnet_creation(self):
        model = get_model("efficientnet_b3", pretrained=False)
        assert model is not None
        x = torch.randn(self.batch_size, 3, 300, 300)
        output = model(x)
        assert output.shape == (self.batch_size, NUM_CLASSES)

    def test_vit_creation(self):
        model = get_model("vit_base", pretrained=False)
        assert model is not None
        x = torch.randn(self.batch_size, 3, 224, 224)
        output = model(x)
        assert output.shape == (self.batch_size, NUM_CLASSES)

    def test_invalid_model(self):
        with pytest.raises(ValueError):
            get_model("invalid_model")

    def test_model_info(self):
        info = get_model_info()
        assert "densenet121" in info
        assert "resnet50" in info
        assert "efficientnet_b3" in info
        assert "vit_base" in info

    def test_disease_classes_count(self):
        assert len(DISEASE_CLASSES) >= 15
        assert "Normal" in DISEASE_CLASSES
        assert "Pneumonia" in DISEASE_CLASSES
