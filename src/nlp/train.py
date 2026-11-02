import csv
import json
import datetime
import sys
from pathlib import Path

# Pastikan root direktori ada di sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)
from src.config import (
    BASE_DIR,
    DATA_DIR,
    MODELS_DIR,
    MODEL_PATH,
    VECTORIZER_PATH,
    METADATA_PATH,
    DB_PATH
)
from src.nlp.preprocessor import preprocess_text
from src.database.db import get_connection

DATASET_PATH = DATA_DIR / "intent_dataset_dummy.csv"

def load_dataset(dataset_path=DATASET_PATH):
    """Membaca dataset intent dari file CSV."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"File dataset tidak ditemukan: {dataset_path}")

    texts = []
    intents = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = (row.get("text") or "").strip()
            intent = (row.get("intent") or "").strip()
            if text and intent:
                texts.append(text)
                intents.append(intent)

    if not texts:
        raise ValueError("Dataset kosong atau tidak memiliki format yang valid.")
    return texts, intents

def train_and_evaluate(dataset_path=DATASET_PATH, db_path=DB_PATH, version_label=None):
    """
    Melatih model klasifikasi intent:
    1. Preprocessing teks
    2. Stratified train-test split (75:25)
    3. Fit TF-IDF Vectorizer hanya pada data latih
    4. Melatih SVM (LinearSVC) dengan CalibratedClassifierCV untuk probabilitas terkalibrasi
    5. Evaluasi pada data uji (Akurasi, Precision, Recall, F1-Score, Confusion Matrix)
    6. Menyimpan model, vectorizer, dan metadata versi
    7. Mencatat versi ke tabel model_versions di database
    """
    print("=" * 60)
    print("MEMULAI PELATIHAN MODEL NLP (TF-IDF + SVM)")
    print("=" * 60)

    # 1. Muat dataset
    raw_texts, labels = load_dataset(dataset_path)
    print(f"Total sampel dataset: {len(raw_texts)}")

    # 2. Preprocessing teks
    processed_texts = [preprocess_text(t) for t in raw_texts]
    unique_intents = sorted(list(set(labels)))
    print(f"Jumlah kategori intent: {len(unique_intents)} ({', '.join(unique_intents)})")

    # 3. Stratified split (75% train, 25% test)
    X_train, X_test, y_train, y_test = train_test_split(
        processed_texts,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels
    )
    print(f"Ukuran Data Latih: {len(X_train)} | Ukuran Data Uji: {len(X_test)}")

    # 4. TF-IDF Vectorizer (Fit HANYA pada data latih sesuai FR-04)
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # 5. Model SVM dengan Kalibrasi Probabilitas (CalibratedClassifierCV)
    base_svc = LinearSVC(dual="auto", random_state=42, C=1.0)
    calibrated_svm = CalibratedClassifierCV(estimator=base_svc, method="sigmoid", cv=3)
    calibrated_svm.fit(X_train_vec, y_train)

    # 6. Evaluasi pada Data Uji
    y_pred = calibrated_svm.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)
    macro_f1, _, _, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
    class_report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    conf_mat = confusion_matrix(y_test, y_pred, labels=unique_intents).tolist()

    print("\nHASIL EVALUASI MODEL:")
    print(f"Akurasi           : {acc * 100:.2f}%")
    print(f"Weighted Precision: {prec * 100:.2f}%")
    print(f"Weighted Recall   : {rec * 100:.2f}%")
    print(f"Weighted F1-Score : {f1 * 100:.2f}%")
    print(f"Macro F1-Score    : {macro_f1 * 100:.2f}%")

    # 7. Simpan artefak model
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    version = version_label or datetime.datetime.now().strftime("v%Y%m%d_%H%M%S")
    timestamp = datetime.datetime.now().isoformat()

    joblib.dump(calibrated_svm, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    metadata = {
        "model_name": "Calibrated_LinearSVC",
        "version": version,
        "trained_at": timestamp,
        "dataset_samples": len(raw_texts),
        "intents": unique_intents,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision_weighted": round(prec, 4),
            "recall_weighted": round(rec, 4),
            "f1_weighted": round(f1, 4),
            "f1_macro": round(macro_f1, 4)
        },
        "classification_report": class_report,
        "confusion_matrix": conf_mat
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nArtefak tersimpan:")
    print(f"- Model: {MODEL_PATH}")
    print(f"- Vectorizer: {VECTORIZER_PATH}")
    print(f"- Metadata: {METADATA_PATH}")

    # 8. Simpan catatan ke tabel model_versions di SQLite
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO model_versions (model_name, version, accuracy, f1_score, artifact_path, trained_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("Calibrated_LinearSVC", version, acc, f1, str(MODEL_PATH), timestamp)
        )
        conn.commit()
        conn.close()
        print("Riwayat model berhasil dicatat ke database.")
    except Exception as e:
        print(f"Catatan: Gagal mencatat versi ke database: {e}")

    return metadata

if __name__ == "__main__":
    train_and_evaluate()
