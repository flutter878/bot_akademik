import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
import numpy as np
from src.config import MODEL_PATH, VECTORIZER_PATH, METADATA_PATH, CONFIDENCE_THRESHOLD
from src.nlp.preprocessor import preprocess_text

_cached_model = None
_cached_vectorizer = None
_cached_metadata = None

def load_model_artifacts(force_reload=False):
    """Memuat artefak model dan vectorizer ke memori (dengan caching)."""
    global _cached_model, _cached_vectorizer, _cached_metadata

    if _cached_model is not None and not force_reload:
        return _cached_model, _cached_vectorizer, _cached_metadata

    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            f"Artefak model belum lengkap. Jalankan 'python src/nlp/train.py' terlebih dahulu. "
            f"Model: {MODEL_PATH.exists()}, Vectorizer: {VECTORIZER_PATH.exists()}"
        )

    _cached_model = joblib.load(MODEL_PATH)
    _cached_vectorizer = joblib.load(VECTORIZER_PATH)

    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            _cached_metadata = json.load(f)
    else:
        _cached_metadata = {}

    return _cached_model, _cached_vectorizer, _cached_metadata

def reload_model():
    """Memuat ulang model setelah proses training baru."""
    return load_model_artifacts(force_reload=True)

def predict_intent(text: str, threshold: float = None) -> tuple[str, float, bool]:
    """
    Memprediksi kategori intent dari teks pengguna:
    1. Preprocessing teks secara konsisten
    2. Transformasi ke representasi TF-IDF menggunakan vectorizer tersimpan
    3. Prediksi probabilitas kelas menggunakan SVM terkalibrasi
    4. Evaluasi threshold keyakinan

    Returns:
        tuple (predicted_intent: str, confidence_score: float, is_confident: bool)
    """
    effective_threshold = threshold if threshold is not None else CONFIDENCE_THRESHOLD

    # Preprocessing
    processed_text = preprocess_text(text)
    if not processed_text:
        return "unknown", 0.0, False

    model, vectorizer, _ = load_model_artifacts()

    # Ekstraksi fitur TF-IDF
    text_vec = vectorizer.transform([processed_text])

    # Jika tidak ada satu pun kata dalam kosakata yang cocok (Out-of-Vocabulary)
    if text_vec.nnz == 0:
        return "unknown", 0.0, False

    # Prediksi probabilitas
    probabilities = model.predict_proba(text_vec)[0]
    classes = model.classes_

    best_idx = int(np.argmax(probabilities))
    best_intent = str(classes[best_idx])
    confidence = float(probabilities[best_idx])

    # Thresholding keyakinan & penanganan kelas unknown (FR-05 & PRD Bagian 5)
    if best_intent == "unknown" or confidence < effective_threshold:
        return "unknown", confidence, False

    return best_intent, confidence, True
