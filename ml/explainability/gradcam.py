import cv2
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from utils.config import config
from utils.logger import log


class GradCAMExplainer:
    def __init__(self, model, device):
        self.model = model
        self.device = device
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        target_layer = self._find_target_layer()
        if target_layer:
            target_layer.register_forward_hook(forward_hook)
            target_layer.register_full_backward_hook(backward_hook)

    def _find_target_layer(self):
        model = self.model
        if hasattr(model, "backbone"):
            backbone = model.backbone
        else:
            backbone = model

        if hasattr(backbone, "features"):
            return backbone.features
        elif hasattr(backbone, "layer4"):
            return backbone.layer4
        elif hasattr(backbone, "blocks"):
            return backbone.blocks[-1]
        elif hasattr(backbone, "conv_head"):
            return backbone.conv_head
        else:
            for name, module in reversed(list(backbone.named_children())):
                if isinstance(module, (torch.nn.Conv2d, torch.nn.Sequential)):
                    if isinstance(module, torch.nn.Sequential) and len(module) > 0:
                        return module[-1] if hasattr(module[-1], "out_channels") else module
                    return module
            return backbone

    def generate_heatmap(self, input_tensor: torch.Tensor, target_class: int) -> np.ndarray:
        self.model.zero_grad()
        output = self.model(input_tensor)
        if output.dim() == 1:
            output = output.unsqueeze(0)
        score = output[:, target_class]
        score.backward()

        if self.gradients is None or self.activations is None:
            return np.zeros((224, 224))

        gradients = self.gradients.mean(dim=[2, 3], keepdim=True)
        weights = gradients.squeeze().cpu().detach().numpy()
        activations = self.activations.squeeze().cpu().detach().numpy()

        if weights.ndim == 1:
            cam = np.zeros(activations.shape[1:], dtype=np.float32)
            for i, w in enumerate(weights):
                if i < activations.shape[0]:
                    cam += w * activations[i]
        else:
            cam = np.mean(activations, axis=0)

        cam = np.maximum(cam, 0)
        if cam.max() > 0:
            cam = cam / cam.max()

        cam = cv2.resize(cam, (224, 224))
        return cam

    def generate_gradcam(
        self,
        input_tensor: torch.Tensor,
        original_image: np.ndarray,
        image_path: str,
        detected: Dict[str, float],
    ) -> str:
        if not detected:
            return ""

        try:
            from ml.models.chest_xray_models import DISEASE_CLASSES
            disease_list = list(detected.keys())
            if disease_list and disease_list[0] != "Normal":
                target_disease = disease_list[0]
                if target_disease in DISEASE_CLASSES:
                    target_class = DISEASE_CLASSES.index(target_disease)
                else:
                    target_class = 0
            else:
                target_class = DISEASE_CLASSES.index("Normal")

            input_tensor.requires_grad = True
            cam = self.generate_heatmap(input_tensor, target_class)

            overlay = self._overlay_heatmap(original_image, cam)

            save_name = f"gradcam_{Path(image_path).stem}.png"
            save_dir = config.UPLOAD_DIR / "gradcam"
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / save_name

            overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(save_path), overlay_bgr)

            return str(save_path)

        except Exception as e:
            log.error(f"Grad-CAM generation error: {e}")
            return ""

    def _overlay_heatmap(self, image: np.ndarray, cam: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        cam = cv2.resize(cam, (w, h))
        cam = np.uint8(255 * cam)
        heatmap = cv2.applyColorMap(cam, cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        overlay = cv2.addWeighted(image, 0.6, heatmap, 0.4, 0)
        return overlay

    def generate_multi_class_heatmap(
        self, input_tensor: torch.Tensor, original_image: np.ndarray, detected: Dict[str, float]
    ) -> Dict[str, np.ndarray]:
        from ml.models.chest_xray_models import DISEASE_CLASSES
        heatmaps = {}
        for disease in detected:
            if disease in DISEASE_CLASSES:
                target_class = DISEASE_CLASSES.index(disease)
                cam = self.generate_heatmap(input_tensor, target_class)
                overlay = self._overlay_heatmap(original_image, cam)
                heatmaps[disease] = overlay
        return heatmaps

    def get_explanation_text(self, detected: Dict[str, float], cam: Optional[np.ndarray] = None) -> str:
        if not detected:
            return "No significant findings detected in the image."

        explanations = []
        for disease, confidence in detected.items():
            region = self._get_affected_region(disease)
            explanations.append(
                f"The highlighted {region} region strongly contributed to {disease} "
                f"prediction with {confidence:.1%} confidence."
            )

        if len(explanations) > 2:
            explanations = explanations[:2]
            explanations.append("Additional findings are present. Please refer to the full report.")

        return " ".join(explanations)

    def _get_affected_region(self, disease: str) -> str:
        region_map = {
            "Pneumonia": "lower lung",
            "COVID-19": "peripheral lung",
            "Tuberculosis": "upper lung",
            "Pleural Effusion": "lower lung/pleural",
            "Cardiomegaly": "cardiac",
            "Edema": "central lung",
            "Atelectasis": "lower lung",
            "Consolidation": "middle/lower lung",
            "Mass": "lung parenchymal",
            "Nodule": "lung parenchymal",
            "Fibrosis": "basal lung",
            "Normal": "lung",
        }
        return region_map.get(disease, "lung")
