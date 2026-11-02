import unittest
import tempfile
import os
import json
from pathlib import Path
from app import create_app
from src.database.db import init_db, seed_default_data

class TestBackendAPI(unittest.TestCase):
    def setUp(self):
        # Setup temporary SQLite database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite")
        self.db_path = Path(self.temp_db.name)
        self.temp_db.close()

        self.app = create_app({
            "TESTING": True,
            "DB_PATH": self.db_path,
            "INIT_DB": True
        })
        self.client = self.app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_chat_input_validation(self):
        # Empty message check (FR-02)
        res_empty = self.client.post("/api/chat", json={"message": "   "})
        self.assertEqual(res_empty.status_code, 400)
        self.assertFalse(res_empty.get_json()["success"])

        # Max length check
        long_message = "a" * 501
        res_long = self.client.post("/api/chat", json={"message": long_message})
        self.assertEqual(res_long.status_code, 400)
        self.assertIn("melebihi batas", res_long.get_json()["error"])

    def test_chat_known_intent_success(self):
        # Pertanyaan yang relevan dengan akademik harus dikenali dan mengembalikan jawaban KB
        res = self.client.post("/api/chat", json={"message": "Kapan jadwal libur semester?"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertFalse(data["fallback"])
        self.assertEqual(data["intent"], "kalender_akademik")
        self.assertIn("[DUMMY]", data["answer"])

    def test_chat_fallback_and_logging(self):
        # Pertanyaan di luar domain harus memicu fallback dan dicatat ke unanswered_questions
        res = self.client.post("/api/chat", json={"message": "Berapa harga tiket pesawat ke luar negeri?"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["fallback"])
        self.assertIn("Maaf, pertanyaan Anda belum dapat saya pahami", data["answer"])

    def test_legacy_tanya_endpoint(self):
        res = self.client.post("/tanya", json={"pertanyaan": "Jadwal kuliah?"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("jawaban", data)

    def test_admin_auth_and_protection(self):
        # Akses tanpa login harus ditolak (401)
        res_unauth = self.client.get("/api/admin/stats")
        self.assertEqual(res_unauth.status_code, 401)

        # Login salah kredensial
        res_wrong = self.client.post("/api/admin/login", json={
            "email": "admin@kampus.local",
            "password": "wrongpassword"
        })
        self.assertEqual(res_wrong.status_code, 401)

        # Login benar
        res_login = self.client.post("/api/admin/login", json={
            "email": "admin@kampus.local",
            "password": "adminpassword123"
        })
        self.assertEqual(res_login.status_code, 200)
        self.assertTrue(res_login.get_json()["success"])

        # Akses stats setelah login
        res_stats = self.client.get("/api/admin/stats")
        self.assertEqual(res_stats.status_code, 200)
        self.assertIn("total_faqs", res_stats.get_json()["data"])

        # Akses intents
        res_intents = self.client.get("/api/admin/intents")
        self.assertEqual(res_intents.status_code, 200)
        intents_data = res_intents.get_json()["data"]
        self.assertGreaterEqual(len(intents_data), 7)

        # Admin CRUD FAQ
        # 1. Add FAQ
        first_intent_id = intents_data[0]["id"]
        res_add = self.client.post("/api/admin/faqs", json={
            "intent_id": first_intent_id,
            "question_example": "Bagaimana jadwal ujian?",
            "answer": "Jadwal ujian diumumkan via portal.",
            "source_reference": "[DUMMY] Uji"
        })
        self.assertEqual(res_add.status_code, 201)
        new_faq_id = res_add.get_json()["faq_id"]

        # 2. Modify FAQ
        res_mod = self.client.put(f"/api/admin/faqs/{new_faq_id}", json={
            "question_example": "Bagaimana jadwal ujian susulan?",
            "answer": "Jadwal ujian susulan hubungi prodi.",
            "is_active": True
        })
        self.assertEqual(res_mod.status_code, 200)

        # 3. Delete FAQ
        res_del = self.client.delete(f"/api/admin/faqs/{new_faq_id}")
        self.assertEqual(res_del.status_code, 200)

        # Logout
        res_logout = self.client.post("/api/admin/logout")
        self.assertEqual(res_logout.status_code, 200)

        # Setelah logout, akses kembali 401
        res_after = self.client.get("/api/admin/stats")
        self.assertEqual(res_after.status_code, 401)

if __name__ == "__main__":
    unittest.main()

