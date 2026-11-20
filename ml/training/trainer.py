import os
import time
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report
)
from tqdm import tqdm
from utils.config import config
from utils.logger import log
from ml.models.chest_xray_models import get_model, DISEASE_CLASSES, NUM_CLASSES


class ModelTrainer:
    def __init__(
        self,
        model_name: str = "densenet121",
        num_classes: int = NUM_CLASSES,
        learning_rate: float = 1e-4,
        weight_decay: float = 1e-5,
        device: Optional[torch.device] = None,
    ):
        self.model_name = model_name
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = get_model(model_name, num_classes=num_classes, pretrained=True).to(self.device)
        self.criterion = nn.BCEWithLogitsLoss()
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(), lr=learning_rate, weight_decay=weight_decay
        )
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=50, eta_min=1e-6
        )
        self.scaler = torch.cuda.amp.GradScaler() if torch.cuda.is_available() else None

        self.best_metric = 0.0
        self.history = {
            "train_loss": [], "val_loss": [],
            "accuracy": [], "precision": [], "recall": [],
            "f1": [], "auc_roc": [],
            "learning_rates": [],
            "epoch_times": [],
        }

    def train_epoch(self, dataloader: DataLoader) -> float:
        self.model.train()
        total_loss = 0.0
        progress = tqdm(dataloader, desc="Training")

        for images, labels in progress:
            images, labels = images.to(self.device), labels.to(self.device)
            self.optimizer.zero_grad()

            if self.scaler:
                with torch.cuda.amp.autocast():
                    outputs = self.model(images)
                    loss = self.criterion(outputs, labels)
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()

            total_loss += loss.item()
            progress.set_postfix({"loss": f"{loss.item():.4f}"})

        return total_loss / len(dataloader)

    def validate(self, dataloader: DataLoader) -> Dict[str, float]:
        self.model.eval()
        total_loss = 0.0
        all_preds, all_labels = [], []

        with torch.no_grad():
            for images, labels in tqdm(dataloader, desc="Validation"):
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                total_loss += loss.item()

                probs = torch.sigmoid(outputs).cpu().numpy()
                all_preds.append(probs)
                all_labels.append(labels.cpu().numpy())

        all_preds = np.vstack(all_preds)
        all_labels = np.vstack(all_labels)

        pred_binary = (all_preds > 0.5).astype(int)

        accuracy = accuracy_score(all_labels, pred_binary)
        precision = precision_score(all_labels, pred_binary, average="macro", zero_division=0)
        recall = recall_score(all_labels, pred_binary, average="macro", zero_division=0)
        f1 = f1_score(all_labels, pred_binary, average="macro", zero_division=0)

        try:
            auc_roc = roc_auc_score(all_labels, all_preds, average="macro", multi_class="ovr")
        except ValueError:
            auc_roc = 0.0

        return {
            "val_loss": total_loss / len(dataloader),
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "auc_roc": auc_roc,
        }

    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 50,
        save_best: bool = True,
    ) -> Dict:
        log.info(f"Starting training {self.model_name} for {epochs} epochs")

        for epoch in range(epochs):
            epoch_start = time.time()

            train_loss = self.train_epoch(train_loader)
            metrics = self.validate(val_loader)
            epoch_time = time.time() - epoch_start

            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(metrics["val_loss"])
            self.history["accuracy"].append(metrics["accuracy"])
            self.history["precision"].append(metrics["precision"])
            self.history["recall"].append(metrics["recall"])
            self.history["f1"].append(metrics["f1"])
            self.history["auc_roc"].append(metrics["auc_roc"])
            self.history["learning_rates"].append(self.scheduler.get_last_lr()[0])
            self.history["epoch_times"].append(epoch_time)

            self.scheduler.step()

            log.info(
                f"Epoch {epoch+1}/{epochs} - "
                f"Loss: {train_loss:.4f}/{metrics['val_loss']:.4f}, "
                f"Acc: {metrics['accuracy']:.4f}, F1: {metrics['f1']:.4f}, "
                f"ROC-AUC: {metrics['auc_roc']:.4f}, Time: {epoch_time:.1f}s"
            )

            if save_best and metrics["f1"] + metrics["auc_roc"] > self.best_metric:
                self.best_metric = metrics["f1"] + metrics["auc_roc"]
                self._save_checkpoint(epoch, metrics)
                log.info(f"New best model saved (F1: {metrics['f1']:.4f}, AUC: {metrics['auc_roc']:.4f})")

        return self.history

    def _save_checkpoint(self, epoch: int, metrics: Dict):
        save_path = config.SAVED_MODELS_DIR / f"{self.model_name}_best.pth"
        torch.save({
            "epoch": epoch,
            "model_name": self.model_name,
            "num_classes": self.num_classes,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "metrics": metrics,
            "history": self.history,
        }, save_path)
        log.info(f"Checkpoint saved: {save_path}")

    def evaluate(self, test_loader: DataLoader) -> Dict:
        self.model.eval()
        all_preds, all_labels = [], []

        with torch.no_grad():
            for images, labels in tqdm(test_loader, desc="Testing"):
                images = images.to(self.device)
                outputs = self.model(images)
                probs = torch.sigmoid(outputs).cpu().numpy()
                all_preds.append(probs)
                all_labels.append(labels.cpu().numpy())

        all_preds = np.vstack(all_preds)
        all_labels = np.vstack(all_labels)
        pred_binary = (all_preds > 0.5).astype(int)

        results = {
            "accuracy": accuracy_score(all_labels, pred_binary),
            "precision": precision_score(all_labels, pred_binary, average="macro", zero_division=0),
            "recall": recall_score(all_labels, pred_binary, average="macro", zero_division=0),
            "f1": f1_score(all_labels, pred_binary, average="macro", zero_division=0),
            "report": classification_report(all_labels, pred_binary, target_names=DISEASE_CLASSES[:self.num_classes], zero_division=0),
        }

        try:
            results["auc_roc"] = roc_auc_score(all_labels, all_preds, average="macro", multi_class="ovr")
        except ValueError:
            results["auc_roc"] = 0.0

        return results


def train_all_models(
    train_loader: DataLoader,
    val_loader: DataLoader,
    test_loader: DataLoader,
    epochs: int = 30,
) -> Dict[str, Dict]:
    model_names = ["densenet121", "efficientnet_b3", "resnet50", "vit_base"]
    results = {}

    for model_name in model_names:
        log.info(f"\n{'='*50}\nTraining {model_name}\n{'='*50}")
        trainer = ModelTrainer(model_name=model_name)
        history = trainer.train(train_loader, val_loader, epochs=epochs)
        eval_results = trainer.evaluate(test_loader)
        results[model_name] = {
            "history": history,
            "evaluation": eval_results,
        }

    best_model = max(results, key=lambda k: results[k]["evaluation"]["f1"])
    log.info(f"Best model: {best_model}")
    return results, best_model
