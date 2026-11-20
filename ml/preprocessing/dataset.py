import cv2
import numpy as np
import albumentations as A
from pathlib import Path
from typing import Tuple, Optional, List
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from utils.logger import log


class ChestXRayDataset(Dataset):
    def __init__(
        self,
        image_paths: List[str],
        labels: Optional[np.ndarray] = None,
        transform=None,
        input_size: int = 224,
        is_training: bool = True,
    ):
        self.image_paths = image_paths
        self.labels = labels
        self.input_size = input_size
        self.is_training = is_training

        if transform is None:
            self.transform = self._get_default_transform()
        else:
            self.transform = transform

    def _get_default_transform(self):
        if self.is_training:
            return A.Compose([
                A.Resize(self.input_size, self.input_size),
                A.RandomBrightnessContrast(brightness_limit=0.1, contrast_limit=0.1, p=0.5),
                A.HorizontalFlip(p=0.3),
                A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.05, rotate_limit=10, p=0.3),
                A.GaussNoise(var_limit=(10.0, 30.0), p=0.2),
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
        else:
            return A.Compose([
                A.Resize(self.input_size, self.input_size),
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = cv2.imread(img_path)
        if image is None:
            image = np.zeros((self.input_size, self.input_size, 3), dtype=np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        augmented = self.transform(image=image)
        image = augmented["image"]
        image = torch.from_numpy(image).permute(2, 0, 1).float()

        if self.labels is not None:
            label = torch.tensor(self.labels[idx], dtype=torch.float32)
            return image, label
        return image


def get_training_transforms(input_size=224):
    return A.Compose([
        A.Resize(input_size, input_size),
        A.RandomBrightnessContrast(brightness_limit=0.15, contrast_limit=0.15, p=0.5),
        A.HorizontalFlip(p=0.3),
        A.VerticalFlip(p=0.05),
        A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.05, rotate_limit=15, p=0.4),
        A.GaussNoise(var_limit=(10.0, 50.0), p=0.2),
        A.CLAHE(clip_limit=2.0, tile_grid_size=(8, 8), p=0.3),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def get_validation_transforms(input_size=224):
    return A.Compose([
        A.Resize(input_size, input_size),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


class Preprocessor:
    @staticmethod
    def remove_noise(image: np.ndarray) -> np.ndarray:
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

    @staticmethod
    def resize(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        return cv2.resize(image, size, interpolation=cv2.INTER_LANCZOS4)

    @staticmethod
    def normalize(image: np.ndarray) -> np.ndarray:
        return image / 255.0

    @staticmethod
    def preprocess_pipeline(image_path: str, input_size: int = 224) -> np.ndarray:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Preprocessor.remove_noise(image)
        image = Preprocessor.enhance_contrast(image)
        image = Preprocessor.resize(image, (input_size, input_size))
        return image


def remove_duplicates(image_paths: List[str], threshold: float = 0.95) -> List[str]:
    from scipy.spatial.distance import cosine
    unique_paths = []
    features = []
    for path in image_paths:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        img = cv2.resize(img, (64, 64)).flatten().astype(np.float32)
        img /= np.linalg.norm(img) + 1e-8
        is_dup = False
        for ft in features:
            if 1 - cosine(img, ft) > threshold:
                is_dup = True
                break
        if not is_dup:
            features.append(img)
            unique_paths.append(path)
    log.info(f"Removed {len(image_paths) - len(unique_paths)} duplicate images")
    return unique_paths


def compute_dataset_stats(image_paths: List[str]) -> dict:
    import pandas as pd
    widths, heights, channels = [], [], []
    for path in image_paths:
        img = cv2.imread(path)
        if img is not None:
            h, w, c = img.shape
            widths.append(w)
            heights.append(h)
            channels.append(c)
    df = pd.DataFrame({"width": widths, "height": heights})
    return {
        "total_images": len(image_paths),
        "avg_width": float(np.mean(widths)),
        "avg_height": float(np.mean(heights)),
        "min_width": int(np.min(widths)),
        "max_width": int(np.max(widths)),
        "min_height": int(np.min(heights)),
        "max_height": int(np.max(heights)),
        "std_width": float(np.std(widths)),
        "std_height": float(np.std(heights)),
    }
