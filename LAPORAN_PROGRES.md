# LAPORAN PROGRES PROYEK CAPSTONE
## Pengembangan Chatbot Layanan Akademik Mahasiswa Berbasis NLP

* **Tanggal Pembaruan:** 2 November 2026
* **Status Progres:** Tahap 1, Tahap 2, dan Tahap 3 Selesai (100% Berhasil Diuji)
* **Basis Kode:** Python 3.14 / Flask 3.1 / Scikit-Learn 1.9 / SQLite

---

### 1. Ringkasan Status Capstone

Proyek ini telah berhasil menyelesaikan tiga tahapan krusial sesuai dokumen PRD:
1. **Tahap 1 (Analisis Repositori & Arsitektur):** Mengubah struktur awal yang monolitik menjadi arsitektur modular standar industri.
2. **Tahap 2 (Backend & Basis Pengetahuan):** Membangun skema database relasional SQLite 5 tabel, sistem proteksi autentikasi admin (hash password), serta penanganan validasi input dan pencatatan fallback otomatis.
3. **Tahap 3 (Pipeline NLP & Model Klasifikasi):** Membangun preprocessing teks Bahasa Indonesia, ekstraksi fitur TF-IDF, melatih model Support Vector Machine (SVM) dengan kalibrasi probabilitas (*Calibrated LinearSVC*), serta menghubungkan modul prediksi (*predictor*) ke endpoint chat.

---

### 2. Rincian Implementasi per Tahap

#### A. Tahap 1: Penataan Arsitektur Modular
Struktur proyek ditata ulang agar rapi, mudah dipelihara, dan siap untuk dipresentasikan dalam sidang:
* `data/`: Dataset intent mandiri dan data benih (seed).
* `models/`: Penyimpanan artefak model machine learning tersimpan.
* `src/database/`: Skema DDL SQLite dan modul Data Access Object (DAO).
* `src/nlp/`: Modul preprocessing, skrip training, dan modul inferensi runtime.
* `src/routes/`: Blueprint API untuk Chat Mahasiswa dan Manajemen Admin.
* `templates/` & `static/`: Antarmuka web mahasiswa dan dashboard admin.
* `tests/`: Rangkaian pengujian otomatis unit & integrasi.

---

#### B. Tahap 2: Basis Data dan Backend
1. **Skema Basis Data (`database.sqlite`):**
   * `admins`: Akun pengelola layanan akademik (password ter-hash via `werkzeug.security`).
   * `intents`: 8 kategori intent akademik (`jadwal_kuliah`, `krs`, `ukt_pembayaran`, `kalender_akademik`, `administrasi`, `kontak_akademik`, `sapaan`, `unknown`).
   * `knowledge_base`: Pertanyaan contoh dan jawaban resmi kampus bertanda `[DUMMY]`.
   * `unanswered_questions`: Log pertanyaan mahasiswa yang tidak terjawab atau dialihkan ke fallback.
   * `model_versions`: Riwayat pelatihan model, versi, tanggal latih, dan metrik akurasi/F1.
2. **Autentikasi & Keamanan:**
   * Session-based authentication untuk admin via `@admin_required`.
   * Pengguna tanpa login ditolak dengan kode respons `401 Unauthorized`.
3. **Validasi Input Mahasiswa:**
   * Penolakan input kosong/spasi (HTTP 400).
   * Pembatasan panjang pesan maksimal 500 karakter (HTTP 400).

---

#### C. Tahap 3: Pipeline NLP & Model Machine Learning
1. **Preprocessing Teks Bahasa Indonesia (`src/nlp/preprocessor.py`):**
   * *Case folding* (mengubah ke huruf kecil).
   * *Cleaning* (menghapus tanda baca berlebih dan karakter non-alfanumerik menggunakan Regex).
   * *Normalisasi Slang/Singkatan* (kamus konversi kata tidak baku mahasiswa, contoh: *kpn* &rarr; *kapan*, *gmn* &rarr; *bagaimana*, *byr* &rarr; *bayar*, *spp* &rarr; *ukt*, *dpa* &rarr; *dosen pembimbing akademik*).
2. **Representasi Fitur TF-IDF (`TfidfVectorizer`):**
   * N-gram range `(1, 2)` (unigram & bigram).
   * Proses `fit` hanya dilakukan pada data latih untuk mencegah *data leakage*.
3. **Klasifikasi Intent SVM Terkalibrasi (`LinearSVC` + `CalibratedClassifierCV`):**
   * Model dilatih menggunakan dataset mandiri `data/intent_dataset_dummy.csv` (108 sampel data).
   * Menggunakan kalibrasi sigmoid untuk menghasilkan probabilitas matematis yang valid untuk penentuan *confidence threshold*.
4. **Hasil Evaluasi Model (Data Uji 25%):**
   * **Akurasi (Accuracy):** 88.89%
   * **Weighted Precision:** 91.48%
   * **Weighted Recall:** 88.89%
   * **Weighted F1-Score:** 87.40%
   * **Macro F1-Score:** 91.25%
5. **Mekanisme Fallback Otomatis:**
   * Pertanyaan dengan kosakata yang sama sekali tidak dikenali (*Out-of-Vocabulary* / `nnz == 0`) atau skor keyakinan di bawah 50% (< 0.50) otomatis dialihkan ke pesan fallback ramah dan dicatat ke tabel `unanswered_questions`.

---

### 3. Hasil Pengujian Otomatis

Rangkaian 16 skenario pengujian unit dan integrasi (`unittest`) berhasil dijalankan dengan hasil **100% lulus (All Green)**:

```text
Ran 16 tests in 6.868s

OK (16 tests passed)
- test_seed_intents_and_admin (Database)
- test_knowledge_base_crud (Database)
- test_unanswered_questions_logging (Database)
- test_dashboard_summary (Database)
- test_health_check (API)
- test_chat_input_validation (API)
- test_chat_known_intent_success (API)
- test_chat_fallback_and_logging (API)
- test_legacy_tanya_endpoint (API)
- test_admin_auth_and_protection (API)
- test_text_cleaning (NLP)
- test_slang_normalization (NLP)
- test_pipeline_consistency (NLP)
- test_artifacts_exist_and_loadable (NLP)
- test_intent_prediction_known_queries (NLP)
- test_intent_prediction_out_of_domain (NLP)
```

---

### 4. Panduan Menjalankan Aplikasi

#### 1. Menjalankan Server Web (Flask)
Pastikan virtual environment aktif:
```powershell
.\.venv\Scripts\python.exe app.py
```

#### 2. Akses Aplikasi
* **Halaman Chat Mahasiswa:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
* **Halaman Dashboard Admin:** [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)
  * **Email Default:** `admin@kampus.local`
  * **Password Default:** `adminpassword123`

#### 3. Menjalankan Pelatihan Ulang Model NLP
Jika Anda memperbarui dataset kalimat di `data/intent_dataset_dummy.csv`:
```powershell
.\.venv\Scripts\python.exe src/nlp/train.py
```

#### 4. Menjalankan Rangkaian Pengujian (Test Suite)
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

---

### 5. Rencana Pekerjaan Selanjutnya (Tahap 4 s/d 7)

1. **Tahap 5 (Peningkatan Antarmuka Mahasiswa):**
   * Menambahkan fitur tombol saran pertanyaan cepat (*suggestion chips*).
   * Menambahkan animasi indikator bot sedang mengetik (*typing indicator*).
   * Menampilkan informasi sumber referensi kebijakan kampus (`source_reference`).
2. **Tahap 6 (Peningkatan Dashboard Admin):**
   * Form interaktif untuk menambah, mengubah, dan menonaktifkan FAQ basis pengetahuan langsung dari browser.
   * Tombol untuk memicu pelatihan ulang model (*retrain model*) langsung dari dashboard admin.
3. **Tahap 7 (Finalisasi & Dokumentasi):**
   * Pembaruan menyeluruh file `README.md`.
   * Rekapitulasi metrik evaluasi untuk bahan penulisan Bab 4/Bab 5 Laporan Capstone.

