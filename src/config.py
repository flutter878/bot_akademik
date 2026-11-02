import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DB_PATH = BASE_DIR / "database.sqlite"

# Keamanan dan Konfigurasi Aplikasi
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-akademik-chatbot-2026")
MAX_INPUT_LENGTH = int(os.environ.get("MAX_INPUT_LENGTH", 500))

# Konfigurasi Model NLP
CONFIDENCE_THRESHOLD = float(os.environ.get("CONFIDENCE_THRESHOLD", 0.50))
MODEL_PATH = MODELS_DIR / "svm_intent_model.joblib"
VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

