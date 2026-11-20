"""Training script for Medical Report AI model training"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import torch
from torch.utils.data import DataLoader, random_split
import numpy as np
from pathlib import Path
from utils.logger import log
from utils.config import config
from ml.models.chest_xray_models import DISEASE_CLASSES, NUM_CLASSES, get_model_info
from ml.preprocessing.dataset import ChestXRayDataset, get_training_transforms, get_validation_transforms
from ml.training.trainer import ModelTrainer, train_all_models
from ml.evaluation.metrics import (
    plot_confusion_matrix, plot_roc_curve, plot_training_history,
    plot_precision_recall_curve, generate_classification_report_text
)


def parse_args():
    parser = argparse.ArgumentParser(description="Train Chest X-Ray Classification Models")
    parser.add_argument("--data-dir", type=str, default="./datasets", help="Dataset directory")
    parser.add_argument("--epochs", type=int, default=30, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--model", type=str, default="densenet121",
                        choices=["densenet121", "efficientnet_b3", "resnet50", "vit_base", "all"],
                        help="Model to train")
    parser.add_argument("--num-workers", type=int, default=4, help="Data loading workers")
    parser.add_argument("--val-split", type=float, default=0.15, help="Validation split ratio")
    parser.add_argument("--test-split", type=float, default=0.15, help="Test split ratio")
    return parser.parse_args()


def main():
    args = parse_args()

    config.init_dirs()
    log.info(f"Starting training with config: {args}")

    log.info(f"Model options available: {list(get_model_info().keys())}")
    for name, info in get_model_info().items():
        log.info(f"  {name}: {info}")

    image_paths = list(Path(args.data_dir).rglob("*.png")) + list(Path(args.data_dir).rglob("*.jpg"))
    if not image_paths:
        log.warning("No images found. Creating synthetic dataset for testing.")
        import cv2
        import numpy as np
        test_dir = Path(args.data_dir) / "test_images"
        test_dir.mkdir(parents=True, exist_ok=True)
        for i in range(100):
            img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            cv2.imwrite(str(test_dir / f"test_{i}.png"), img)
        image_paths = list(test_dir.rglob("*.png"))

    log.info(f"Found {len(image_paths)} images")

    num_labels = NUM_CLASSES
    labels = np.random.randint(0, 2, (len(image_paths), num_labels))

    n = len(image_paths)
    n_val = int(n * args.val_split)
    n_test = int(n * args.test_split)
    n_train = n - n_val - n_test

    train_paths = image_paths[:n_train]
    val_paths = image_paths[n_train:n_train + n_val]
    test_paths = image_paths[n_train + n_val:]

    train_labels = labels[:n_train]
    val_labels = labels[n_train:n_train + n_val]
    test_labels = labels[n_train + n_val:]

    log.info(f"Train: {len(train_paths)}, Val: {len(val_paths)}, Test: {len(test_paths)}")

    train_dataset = ChestXRayDataset(
        train_paths, train_labels,
        transform=get_training_transforms(),
        is_training=True,
    )
    val_dataset = ChestXRayDataset(
        val_paths, val_labels,
        transform=get_validation_transforms(),
        is_training=False,
    )
    test_dataset = ChestXRayDataset(
        test_paths, test_labels,
        transform=get_validation_transforms(),
        is_training=False,
    )

    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size,
        shuffle=True, num_workers=args.num_workers, pin_memory=True,
    )
    val_loader = DataLoader(
        val_dataset, batch_size=args.batch_size,
        shuffle=False, num_workers=args.num_workers,
    )
    test_loader = DataLoader(
        test_dataset, batch_size=args.batch_size,
        shuffle=False, num_workers=args.num_workers,
    )

    if args.model == "all":
        results, best_model = train_all_models(train_loader, val_loader, test_loader, epochs=args.epochs)
        log.info(f"Best model overall: {best_model}")
    else:
        trainer = ModelTrainer(
            model_name=args.model,
            num_classes=num_labels,
            learning_rate=args.lr,
        )
        history = trainer.train(train_loader, val_loader, epochs=args.epochs)
        eval_results = trainer.evaluate(test_loader)

        log.info(f"Evaluation results: {eval_results}")
        log.info(f"\n{eval_results.get('report', '')}")

        plot_training_history(history)

    log.info("Training completed!")


if __name__ == "__main__":
    main()
