import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

def generate_uuid() -> str:
    return str(uuid.uuid4())

def generate_patient_id() -> str:
    return f"PAT-{uuid.uuid4().hex[:8].upper()}"

def hash_image(image_bytes: bytes) -> str:
    return hashlib.md5(image_bytes).hexdigest()

def validate_image_extension(filename: str) -> bool:
    allowed = {"png", "jpeg", "jpg"}
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in allowed

def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def format_timestamp(dt: Optional[datetime] = None) -> str:
    dt = dt or datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def calculate_confidence_color(confidence: float) -> str:
    if confidence >= 0.8:
        return "#16A34A"
    elif confidence >= 0.5:
        return "#F59E0B"
    return "#DC2626"
