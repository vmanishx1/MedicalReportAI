import pytest
import cv2
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.preprocessing.dataset import Preprocessor, ChestXRayDataset


class TestPreprocessor:
    def setup_method(self):
        self.preprocessor = Preprocessor()
        self.test_image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

    def test_noise_removal(self):
        noisy = self.test_image + np.random.randint(0, 30, self.test_image.shape, dtype=np.uint8)
        cleaned = self.preprocessor.remove_noise(noisy)
        assert cleaned.shape == noisy.shape

    def test_contrast_enhancement(self):
        enhanced = self.preprocessor.enhance_contrast(self.test_image)
        assert enhanced.shape == self.test_image.shape

    def test_resize(self):
        resized = self.preprocessor.resize(self.test_image, (224, 224))
        assert resized.shape == (224, 224, 3)

    def test_normalize(self):
        normalized = self.preprocessor.normalize(self.test_image.astype(np.float32))
        assert normalized.max() <= 1.0
        assert normalized.min() >= 0.0


class TestDataset:
    def test_dataset_creation(self, tmp_path):
        img_path = tmp_path / "test.png"
        cv2.imwrite(str(img_path), np.random.randint(0, 255, (224, 224, 3)))

        dataset = ChestXRayDataset(
            image_paths=[str(img_path)],
            labels=np.array([[1, 0, 0]]),
            input_size=224,
            is_training=True,
        )
        assert len(dataset) == 1
        image, label = dataset[0]
        assert image.shape == (3, 224, 224)
        assert label.shape == (3,)
