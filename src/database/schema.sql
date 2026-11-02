-- Skema Basis Data SQLite untuk Chatbot Layanan Akademik Mahasiswa
-- Sesuai PRD Bagian 10

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS intents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_id INTEGER NOT NULL,
    question_example TEXT NOT NULL,
    answer TEXT NOT NULL,
    source_reference TEXT DEFAULT '[DUMMY] Pedoman Akademik Internal',
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (intent_id) REFERENCES intents(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS unanswered_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    predicted_intent TEXT,
    confidence_score REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    version TEXT NOT NULL,
    accuracy REAL,
    f1_score REAL,
    artifact_path TEXT,
    trained_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indeks untuk efisiensi kueri
CREATE INDEX IF NOT EXISTS idx_intents_code ON intents(code);
CREATE INDEX IF NOT EXISTS idx_kb_intent_id ON knowledge_base(intent_id);
CREATE INDEX IF NOT EXISTS idx_kb_is_active ON knowledge_base(is_active);

