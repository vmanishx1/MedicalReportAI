import torch
import torch.nn as nn
import torchvision.models as models
import timm


DISEASE_CLASSES = [
    "Atelectasis", "Cardiomegaly", "Consolidation", "Edema",
    "Effusion", "Emphysema", "Fibrosis", "Hernia",
    "Infiltration", "Mass", "Nodule", "Pleural_Thickening",
    "Pneumonia", "Pneumothorax", "Tuberculosis", "COVID-19",
    "Normal"
]

NUM_CLASSES = len(DISEASE_CLASSES)


class BaseChestXRayModel(nn.Module):
    def __init__(self, backbone, num_classes=NUM_CLASSES):
        super().__init__()
        self.backbone = backbone
        self.num_classes = num_classes

    def forward(self, x):
        return self.backbone(x)

    def get_features(self, x):
        return self.backbone(x)


def create_efficientnet_b3(num_classes=NUM_CLASSES, pretrained=True):
    if pretrained:
        model = timm.create_model("efficientnet_b3", pretrained=True)
    else:
        model = timm.create_model("efficientnet_b3", pretrained=False)
    in_features = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(512, num_classes),
    )
    return BaseChestXRayModel(model, num_classes)


def create_resnet50(num_classes=NUM_CLASSES, pretrained=True):
    model = models.resnet50(weights="IMAGENET1K_V2" if pretrained else None)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(512, num_classes),
    )
    return BaseChestXRayModel(model, num_classes)


def create_densenet121(num_classes=NUM_CLASSES, pretrained=True):
    model = models.densenet121(weights="IMAGENET1K_V1" if pretrained else None)
    in_features = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(512, num_classes),
    )
    return BaseChestXRayModel(model, num_classes)


def create_vit_base(num_classes=NUM_CLASSES, pretrained=True):
    if pretrained:
        model = timm.create_model("vit_base_patch16_224", pretrained=True)
    else:
        model = timm.create_model("vit_base_patch16_224", pretrained=False)
    in_features = model.head.in_features
    model.head = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(512, num_classes),
    )
    return BaseChestXRayModel(model, num_classes)


def get_model(model_name: str, num_classes=NUM_CLASSES, pretrained=True):
    models_map = {
        "efficientnet_b3": create_efficientnet_b3,
        "resnet50": create_resnet50,
        "densenet121": create_densenet121,
        "vit_base": create_vit_base,
    }
    creator = models_map.get(model_name.lower())
    if creator is None:
        raise ValueError(f"Unknown model: {model_name}. Choose from {list(models_map.keys())}")
    return creator(num_classes=num_classes, pretrained=pretrained)


def get_model_info():
    return {
        "efficientnet_b3": {
            "name": "EfficientNet-B3",
            "params_m": 12.0,
            "input_size": 300,
            "description": "EfficientNet-B3 with custom classifier head"
        },
        "resnet50": {
            "name": "ResNet-50",
            "params_m": 25.6,
            "input_size": 224,
            "description": "ResNet-50 with custom classifier head"
        },
        "densenet121": {
            "name": "DenseNet-121",
            "params_m": 8.0,
            "input_size": 224,
            "description": "DenseNet-121 with custom classifier head"
        },
        "vit_base": {
            "name": "Vision Transformer (ViT-B/16)",
            "params_m": 86.0,
            "input_size": 224,
            "description": "ViT-Base with custom classifier head"
        },
    }
