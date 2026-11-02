import unittest
import tempfile
import os
from pathlib import Path
from src.database.db import (
    init_db,
    seed_default_data,
    get_all_intents,
    get_all_faqs,
    get_active_faq_by_intent_code,
    create_faq,
    update_faq,
    delete_faq,
    log_unanswered_question,
    get_unanswered_questions,
    get_admin_by_email,
    get_dashboard_summary
)

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Gunakan temporary database untuk isolasi pengujian
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite")
        self.db_path = self.temp_db.name
        self.temp_db.close()
        init_db(self.db_path)
        seed_default_data(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_seed_intents_and_admin(self):
        intents = get_all_intents(self.db_path)
        self.assertGreaterEqual(len(intents), 7)
        intent_codes = [i["code"] for i in intents]
        self.assertIn("jadwal_kuliah", intent_codes)
        self.assertIn("krs", intent_codes)

        admin = get_admin_by_email("admin@kampus.local", self.db_path)
        self.assertIsNotNone(admin)
        self.assertEqual(admin["name"], "Administrator Akademik")

    def test_knowledge_base_crud(self):
        # Cek default FAQ dummy
        faqs = get_all_faqs(db_path=self.db_path)
        self.assertGreaterEqual(len(faqs), 5)

        # Get active by intent code
        faq_krs = get_active_faq_by_intent_code("krs", self.db_path)
        self.assertIsNotNone(faq_krs)
        self.assertIn("[DUMMY]", faq_krs["answer"])

        # Create new FAQ
        new_id = create_faq(
            intent_id=faq_krs["intent_id"],
            question_example="Pertanyaan Tambahan Uji",
            answer="Jawaban Uji [DUMMY]",
            source_reference="Pedoman Uji",
            is_active=1,
            db_path=self.db_path
        )
        self.assertIsNotNone(new_id)

        # Update FAQ
        updated = update_faq(
            faq_id=new_id,
            intent_id=faq_krs["intent_id"],
            question_example="Pertanyaan Tambahan Diubah",
            answer="Jawaban Diubah",
            source_reference="Pedoman Uji",
            is_active=0,
            db_path=self.db_path
        )
        self.assertTrue(updated)

        # Delete FAQ
        deleted = delete_faq(new_id, self.db_path)
        self.assertTrue(deleted)

    def test_unanswered_questions_logging(self):
        log_id = log_unanswered_question("Berapa biaya asrama mahasiswa?", "unknown", 0.12, self.db_path)
        self.assertIsNotNone(log_id)

        logs = get_unanswered_questions(limit=10, db_path=self.db_path)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["question"], "Berapa biaya asrama mahasiswa?")

    def test_dashboard_summary(self):
        summary = get_dashboard_summary(self.db_path)
        self.assertIn("total_faqs", summary)
        self.assertIn("total_intents", summary)
        self.assertGreaterEqual(summary["total_intents"], 7)

if __name__ == "__main__":
    unittest.main()

