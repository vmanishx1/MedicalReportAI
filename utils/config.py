import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "medai_secret_key_change_in_production_2026")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/backend/database/medai.db")
    POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/medai")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "saved_models" / "best_model.pth"))
    REPORT_MODEL_PATH = os.getenv("REPORT_MODEL_PATH", str(BASE_DIR / "saved_models" / "report_model.pth"))
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "20971520"))
    ALLOWED_EXTENSIONS = {"png", "jpeg", "jpg"}
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
    REPORT_DIR = Path(os.getenv("REPORT_DIR", str(BASE_DIR / "reports")))
    SAVED_MODELS_DIR = BASE_DIR / "saved_models"

    @classmethod
    def init_dirs(cls):
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORT_DIR.mkdir(parents=True, exist_ok=True)
        cls.SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)


config = Config()
