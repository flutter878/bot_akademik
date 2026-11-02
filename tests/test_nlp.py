import unittest
import json
from pathlib import Path
from src.nlp.preprocessor import clean_text, normalize_slang, preprocess_text
from src.nlp.predictor import predict_intent, load_model_artifacts
from src.config import MODEL_PATH, VECTORIZER_PATH, METADATA_PATH

class TestNLPPipeline(unittest.TestCase):
    def test_text_cleaning(self):
        raw = "Halo! Kapan JADWAL kuliah dibuka??? #akademik 123"
        cleaned = clean_text(raw)
        self.assertEqual(cleaned, "halo kapan jadwal kuliah dibuka akademik 123")

    def test_slang_normalization(self):
        slang_input = "gmn kpn sy byr spp pake m-banking min"
        # after clean: gmn kpn sy byr spp pake m banking min
        cleaned = clean_text(slang_input)
        normalized = normalize_slang(cleaned)
        self.assertIn("bagaimana", normalized)
        self.assertIn("kapan", normalized)
        self.assertIn("saya", normalized)
        self.assertIn("bayar", normalized)
        self.assertIn("ukt", normalized) # spp -> ukt
        self.assertIn("admin", normalized)

    def test_pipeline_consistency(self):
        res1 = preprocess_text("Bagaimana Cara Mengisi KRS Online?")
        res2 = preprocess_text("bagaimana cara mengisi krs online?")
        self.assertEqual(res1, res2)

    def test_artifacts_exist_and_loadable(self):
        self.assertTrue(MODEL_PATH.exists(), "File model SVM harus ada.")
        self.assertTrue(VECTORIZER_PATH.exists(), "File TF-IDF vectorizer harus ada.")
        self.assertTrue(METADATA_PATH.exists(), "File metadata model harus ada.")

        model, vectorizer, metadata = load_model_artifacts()
        self.assertIsNotNone(model)
        self.assertIsNotNone(vectorizer)
        self.assertIn("metrics", metadata)
        self.assertGreaterEqual(metadata["metrics"]["accuracy"], 0.75)

    def test_intent_prediction_known_queries(self):
        test_cases = [
            ("Kapan pengisian krs online dibuka?", "krs"),
            ("Bagaimana cara melihat jadwal kuliah semester baru?", "jadwal_kuliah"),
            ("Prosedur pembayaran UKT dan batas akhir bayar", "ukt_pembayaran"),
            ("Halo selamat pagi admin", "sapaan"),
            ("Apa syarat surat keterangan mahasiswa aktif kuliah?", "administrasi"),
            ("Di mana download kalender akademik?", "kalender_akademik"),
            ("Bagaimana menghubungi kontak layanan akademik?", "kontak_akademik")
        ]

        for query, expected_intent in test_cases:
            with self.subTest(query=query):
                intent, confidence, is_confident = predict_intent(query)
                self.assertTrue(is_confident, f"Harus meyakinkan untuk query: '{query}', confidence: {confidence}")
                self.assertEqual(intent, expected_intent, f"Salah prediksi untuk '{query}': dapat {intent}, harusnya {expected_intent}")

    def test_intent_prediction_out_of_domain(self):
        # Pertanyaan di luar ranah akademik kampus harus ditandai tidak meyakinkan / unknown
        ood_query = "Bagaimana resep memasak rendang daging sapi padang enak?"
        intent, confidence, is_confident = predict_intent(ood_query, threshold=0.40)
        # Sistem harus menandai query ini sebagai unknown atau confidence rendah
        self.assertFalse(is_confident, f"Query out of domain tidak boleh percaya diri: {confidence}")
        self.assertEqual(intent, "unknown")

if __name__ == "__main__":
    unittest.main()

