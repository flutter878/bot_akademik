import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash
from src.config import DB_PATH

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_connection(db_path=None):
    """Membuka koneksi ke database SQLite dengan row_factory Row dan foreign keys aktif."""
    target_path = Path(db_path) if db_path else DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path=None):
    """Inisialisasi tabel berdasarkan file schema.sql."""
    conn = get_connection(db_path)
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()

def seed_default_data(db_path=None):
    """Menyisipkan data awal (Admin, Kategori Intent, dan FAQ Dummy) jika tabel masih kosong."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        # 1. Seed Admin Default
        cursor.execute("SELECT COUNT(*) AS total FROM admins")
        if cursor.fetchone()["total"] == 0:
            default_password_hash = generate_password_hash("adminpassword123")
            cursor.execute(
                """
                INSERT INTO admins (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                ("Administrator Akademik", "admin@kampus.local", default_password_hash)
            )

        # 2. Seed Intent Kategori Awal (PRD Bagian 5)
        cursor.execute("SELECT COUNT(*) AS total FROM intents")
        if cursor.fetchone()["total"] == 0:
            default_intents = [
                ("jadwal_kuliah", "Jadwal Perkuliahan", "Informasi jadwal kuliah, ruangan, dan kelas"),
                ("krs", "Kartu Rencana Studi", "Informasi pengisian, revisi, dan syarat KRS"),
                ("ukt_pembayaran", "UKT dan Pembayaran", "Informasi biaya kuliah, tagihan, dan metode bayar"),
                ("kalender_akademik", "Kalender Akademik", "Tanggal penting semester, libur, dan masa ujian"),
                ("administrasi", "Administrasi Akademik", "Surat keterangan aktif, cuti kuliah, dan legalisir"),
                ("kontak_akademik", "Kontak Layanan Akademik", "Kontak resmi, lokasi helpdesk, dan jam layanan"),
                ("sapaan", "Sapaan Umum", "Salam, pembuka percakapan, dan basa-basi santai"),
                ("unknown", "Tidak Dikenali", "Kategori fallback untuk pertanyaan di luar domain")
            ]
            cursor.executemany(
                """
                INSERT INTO intents (code, name, description)
                VALUES (?, ?, ?)
                """,
                default_intents
            )

        # 3. Seed Knowledge Base Dummy (Bertanda [DUMMY] sesuai PRD)
        cursor.execute("SELECT COUNT(*) AS total FROM knowledge_base")
        if cursor.fetchone()["total"] == 0:
            # Dapatkan pemetaan code -> id
            cursor.execute("SELECT id, code FROM intents")
            intent_map = {row["code"]: row["id"] for row in cursor.fetchall()}

            default_faqs = [
                (
                    intent_map.get("jadwal_kuliah"),
                    "Bagaimana cara melihat jadwal kuliah?",
                    "[DUMMY] Jadwal kuliah semester aktif dapat dilihat melalui portal akademik (SIAKAD) pada menu Akademik > Jadwal Kuliah seminggu sebelum perkuliahan dimulai.",
                    "[DUMMY] Panduan SIAKAD 2026",
                    1
                ),
                (
                    intent_map.get("krs"),
                    "Kapan pengisian KRS dibuka dan bagaimana prosedurnya?",
                    "[DUMMY] Pengisian KRS dibuka sesuai jadwal kalender akademik melalui SIAKAD. Pastikan tagihan UKT telah diselesaikan dan konsultasikan rencana studi dengan Dosen Pembimbing Akademik.",
                    "[DUMMY] Panduan KRS Online",
                    1
                ),
                (
                    intent_map.get("ukt_pembayaran"),
                    "Bagaimana prosedur pembayaran UKT?",
                    "[DUMMY] Pembayaran UKT dilakukan melalui Virtual Account bank mitra kampus (ATM/Mobile Banking) dengan memasukkan NIM/Kode Tagihan yang tertera pada portal keuangan mahasiswa.",
                    "[DUMMY] Buku Panduan Keuangan",
                    1
                ),
                (
                    intent_map.get("kalender_akademik"),
                    "Kapan semester dimulai dan di mana melihat kalender akademik?",
                    "[DUMMY] Kalender akademik resmi dapat diunduh pada website resmi universitas di bagian menu Pengumuman Akademik.",
                    "[DUMMY] Kalender Akademik 2026",
                    1
                ),
                (
                    intent_map.get("administrasi"),
                    "Apa syarat pengajuan surat keterangan aktif kuliah?",
                    "[DUMMY] Pengajuan surat aktif kuliah memerlukan bukti KRS semester berjalan dan slip bukti bayar UKT. Pengajuan diajukan secara online melalui menu Layanan Surat SIAKAD.",
                    "[DUMMY] SOP Layanan Administrasi",
                    1
                ),
                (
                    intent_map.get("kontak_akademik"),
                    "Bagaimana menghubungi bagian layanan akademik?",
                    "[DUMMY] Layanan Akademik Kampus dapat dihubungi melalui email akademik@kampus.local atau kunjungi helpdesk Gedung Pelayanan Lt. 1 pada hari Senin-Jumat pukul 08.00-15.00 WIB.",
                    "[DUMMY] Direktori Kontak Kampus",
                    1
                ),
                (
                    intent_map.get("sapaan"),
                    "Halo / Selamat Pagi",
                    "Halo! Saya adalah asisten virtual layanan akademik kampus. Silakan tanyakan hal seputar jadwal kuliah, KRS, UKT, kalender akademik, atau administrasi.",
                    "[DUMMY] Standar Respons Chatbot",
                    1
                )
            ]

            cursor.executemany(
                """
                INSERT INTO knowledge_base (intent_id, question_example, answer, source_reference, is_active)
                VALUES (?, ?, ?, ?, ?)
                """,
                default_faqs
            )

        conn.commit()
    finally:
        conn.close()

# ==========================================
# DAO Helpers (Fungsi Akses Data)
# ==========================================

# --- Admin & Auth ---
def get_admin_by_email(email, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE email = ?", (email.strip().lower(),))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_admin_by_id(admin_id, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, created_at FROM admins WHERE id = ?", (admin_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

# --- Intent Categories ---
def get_all_intents(db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, name, description, created_at FROM intents ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_intent_by_code(code, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, name, description FROM intents WHERE code = ?", (code,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

# --- Knowledge Base / FAQ ---
def get_all_faqs(intent_id=None, active_only=False, search=None, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        query = """
            SELECT kb.id, kb.intent_id, i.code AS intent_code, i.name AS intent_name,
                   kb.question_example, kb.answer, kb.source_reference, kb.is_active,
                   kb.created_at, kb.updated_at
            FROM knowledge_base kb
            JOIN intents i ON kb.intent_id = i.id
            WHERE 1=1
        """
        params = []
        if active_only:
            query += " AND kb.is_active = 1"
        if intent_id:
            query += " AND kb.intent_id = ?"
            params.append(intent_id)
        if search:
            query += " AND (kb.question_example LIKE ? OR kb.answer LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term])

        query += " ORDER BY kb.id DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_faq_by_id(faq_id, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT kb.id, kb.intent_id, i.code AS intent_code, i.name AS intent_name,
                   kb.question_example, kb.answer, kb.source_reference, kb.is_active,
                   kb.created_at, kb.updated_at
            FROM knowledge_base kb
            JOIN intents i ON kb.intent_id = i.id
            WHERE kb.id = ?
            """,
            (faq_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_active_faq_by_intent_code(intent_code, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT kb.id, kb.intent_id, i.code AS intent_code, i.name AS intent_name,
                   kb.question_example, kb.answer, kb.source_reference, kb.is_active
            FROM knowledge_base kb
            JOIN intents i ON kb.intent_id = i.id
            WHERE i.code = ? AND kb.is_active = 1
            ORDER BY kb.id DESC
            LIMIT 1
            """,
            (intent_code,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def create_faq(intent_id, question_example, answer, source_reference="[DUMMY] Pedoman Internal", is_active=1, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO knowledge_base (intent_id, question_example, answer, source_reference, is_active)
            VALUES (?, ?, ?, ?, ?)
            """,
            (intent_id, question_example.strip(), answer.strip(), source_reference.strip(), int(is_active))
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def update_faq(faq_id, intent_id, question_example, answer, source_reference, is_active, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE knowledge_base
            SET intent_id = ?, question_example = ?, answer = ?, source_reference = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (intent_id, question_example.strip(), answer.strip(), source_reference.strip(), int(is_active), faq_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_faq(faq_id, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM knowledge_base WHERE id = ?", (faq_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# --- Fallback / Unanswered Questions Logging ---
def log_unanswered_question(question, predicted_intent="unknown", confidence_score=0.0, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO unanswered_questions (question, predicted_intent, confidence_score)
            VALUES (?, ?, ?)
            """,
            (question.strip(), predicted_intent, float(confidence_score))
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_unanswered_questions(limit=100, db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, question, predicted_intent, confidence_score, created_at
            FROM unanswered_questions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

# --- Dashboard Summary ---
def get_dashboard_summary(db_path=None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM knowledge_base")
        total_faqs = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM knowledge_base WHERE is_active = 1")
        active_faqs = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM intents")
        total_intents = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM unanswered_questions")
        total_unanswered = cursor.fetchone()["total"]

        return {
            "total_faqs": total_faqs,
            "active_faqs": active_faqs,
            "total_intents": total_intents,
            "total_unanswered": total_unanswered
        }
    finally:
        conn.close()

