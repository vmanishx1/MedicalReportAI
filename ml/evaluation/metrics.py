import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix, roc_curve, auc,
    precision_recall_curve, classification_report
)
from typing import Dict, List, Optional, Tuple
from utils.logger import log

EVAL_DIR = Path(__file__).resolve().parent.parent.parent / "reports" / "evaluation"


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: List[str],
    save_path: Optional[str] = None,
    title: str = "Confusion Matrix",
) -> str:
    if save_path is None:
        EVAL_DIR.mkdir(parents=True, exist_ok=True)
        save_path = str(EVAL_DIR / "confusion_matrix.png")

    if y_pred.ndim > 1 and y_pred.shape[1] > 1:
        y_pred = np.argmax(y_pred, axis=1)
    if y_true.ndim > 1 and y_true.shape[1] > 1:
        y_true = np.argmax(y_true, axis=1)

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=class_names, yticklabels=class_names,
    )
    plt.title(title, fontsize=16, pad=20)
    plt.xlabel("Predicted", fontsize=12)
    plt.ylabel("Actual", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Confusion matrix saved: {save_path}")
    return save_path


def plot_roc_curve(
    y_true: np.ndarray,
    y_score: np.ndarray,
    class_names: List[str],
    save_path: Optional[str] = None,
    title: str = "ROC Curves",
) -> str:
    if save_path is None:
        EVAL_DIR.mkdir(parents=True, exist_ok=True)
        save_path = str(EVAL_DIR / "roc_curve.png")

    plt.figure(figsize=(12, 8))
    for i in range(min(len(class_names), y_score.shape[1])):
        fpr, tpr, _ = roc_curve(y_true[:, i], y_score[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f"{class_names[i]} (AUC = {roc_auc:.3f})")

    plt.plot([0, 1], [0, 1], "k--", label="Random")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)
    plt.title(title, fontsize=16, pad=20)
    plt.legend(loc="lower right", fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"ROC curve saved: {save_path}")
    return save_path


def plot_precision_recall_curve(
    y_true: np.ndarray,
    y_score: np.ndarray,
    class_names: List[str],
    save_path: Optional[str] = None,
) -> str:
    if save_path is None:
        EVAL_DIR.mkdir(parents=True, exist_ok=True)
        save_path = str(EVAL_DIR / "pr_curve.png")

    plt.figure(figsize=(12, 8))
    for i in range(min(len(class_names), y_score.shape[1])):
        precision, recall, _ = precision_recall_curve(y_true[:, i], y_score[:, i])
        plt.plot(recall, precision, label=class_names[i])

    plt.xlabel("Recall", fontsize=12)
    plt.ylabel("Precision", fontsize=12)
    plt.title("Precision-Recall Curves", fontsize=16, pad=20)
    plt.legend(loc="best", fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    return save_path


def plot_training_history(
    history: Dict,
    save_path: Optional[str] = None,
) -> Dict[str, str]:
    if save_path is None:
        EVAL_DIR.mkdir(parents=True, exist_ok=True)
        save_path = str(EVAL_DIR / "training_history.png")

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    epochs_range = range(1, len(history["train_loss"]) + 1)

    axes[0, 0].plot(epochs_range, history["train_loss"], "b-", label="Train Loss")
    axes[0, 0].plot(epochs_range, history["val_loss"], "r-", label="Val Loss")
    axes[0, 0].set_title("Loss Curves")
    axes[0, 0].set_xlabel("Epochs")
    axes[0, 0].set_ylabel("Loss")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(epochs_range, history["accuracy"], "g-", label="Accuracy")
    axes[0, 1].set_title("Accuracy")
    axes[0, 1].set_xlabel("Epochs")
    axes[0, 1].set_ylabel("Accuracy")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[0, 2].plot(epochs_range, history["f1"], "m-", label="F1 Score")
    axes[0, 2].set_title("F1 Score")
    axes[0, 2].set_xlabel("Epochs")
    axes[0, 2].set_ylabel("F1")
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)

    axes[1, 0].plot(epochs_range, history["precision"], "c-", label="Precision")
    axes[1, 0].plot(epochs_range, history["recall"], "y-", label="Recall")
    axes[1, 0].set_title("Precision & Recall")
    axes[1, 0].set_xlabel("Epochs")
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(epochs_range, history["auc_roc"], "orange", label="ROC AUC")
    axes[1, 1].set_title("ROC AUC")
    axes[1, 1].set_xlabel("Epochs")
    axes[1, 1].set_ylabel("AUC")
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    axes[1, 2].plot(epochs_range, history["learning_rates"], "purple", label="LR")
    axes[1, 2].set_title("Learning Rate")
    axes[1, 2].set_xlabel("Epochs")
    axes[1, 2].set_ylabel("LR")
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)

    plt.suptitle("Training History", fontsize=18, y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

    saved = {"training_history": save_path}

    loss_path = str(EVAL_DIR / "loss_curve.png")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(epochs_range, history["train_loss"], "b-", label="Train Loss", linewidth=2)
    ax2.plot(epochs_range, history["val_loss"], "r-", label="Val Loss", linewidth=2)
    ax2.set_title("Loss Curve", fontsize=16)
    ax2.set_xlabel("Epochs", fontsize=12)
    ax2.set_ylabel("Loss", fontsize=12)
    ax2.legend(fontsize=12)
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(loss_path, dpi=150, bbox_inches="tight")
    plt.close()
    saved["loss_curve"] = loss_path

    acc_path = str(EVAL_DIR / "accuracy_curve.png")
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.plot(epochs_range, history["accuracy"], "g-", label="Accuracy", linewidth=2)
    ax3.set_title("Accuracy Curve", fontsize=16)
    ax3.set_xlabel("Epochs", fontsize=12)
    ax3.set_ylabel("Accuracy", fontsize=12)
    ax3.legend(fontsize=12)
    ax3.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(acc_path, dpi=150, bbox_inches="tight")
    plt.close()
    saved["accuracy_curve"] = acc_path

    return saved


def generate_classification_report_text(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: List[str],
    save_path: Optional[str] = None,
) -> str:
    if save_path is None:
        EVAL_DIR.mkdir(parents=True, exist_ok=True)
        save_path = str(EVAL_DIR / "classification_report.txt")

    if y_pred.ndim > 1:
        y_pred = np.argmax(y_pred, axis=1)
    if y_true.ndim > 1:
        y_true = np.argmax(y_true, axis=1)

    report = classification_report(y_true, y_pred, target_names=class_names, zero_division=0)
    with open(save_path, "w") as f:
        f.write(report)
    log.info(f"Classification report saved: {save_path}")
    return save_path
