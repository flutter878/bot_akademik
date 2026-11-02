# PRD --- Pengembangan Chatbot Layanan Akademik Mahasiswa Berbasis NLP

**Versi:** 1.0\
**Status:** Draft\
**Bahasa:** Indonesia\
**Produk:** Aplikasi web chatbot layanan akademik

## 1. Ringkasan Produk

Aplikasi web yang memungkinkan mahasiswa bertanya tentang layanan
akademik menggunakan Bahasa Indonesia. Sistem memproses pertanyaan
dengan Natural Language Processing (NLP), mengklasifikasikan maksud
pertanyaan (*intent*) menggunakan TF-IDF dan Support Vector Machine
(SVM), lalu mengambil jawaban dari basis pengetahuan akademik yang
dikelola admin.

Chatbot hanya boleh menjawab berdasarkan informasi yang tersedia dan
telah diverifikasi. Jika pertanyaan tidak dikenali atau jawabannya tidak
tersedia, chatbot menampilkan respons fallback dan arahan ke layanan
akademik.

## 2. Latar Belakang dan Tujuan

Mahasiswa membutuhkan akses cepat terhadap informasi jadwal kuliah, KRS,
UKT, kalender akademik, dan administrasi. Layanan manual dapat
menyebabkan pertanyaan berulang dan waktu tunggu.

Tujuan: 1. Menyediakan layanan tanya jawab akademik otomatis. 2.
Mengidentifikasi intent pertanyaan berbahasa Indonesia. 3. Menyampaikan
jawaban secara konsisten dari basis pengetahuan. 4. Mengarahkan
pertanyaan yang belum dapat dijawab ke kanal resmi. 5. Memudahkan admin
memperbarui informasi.

## 3. Pengguna dan Hak Akses

### Mahasiswa

-   Membuka halaman chatbot.
-   Mengirim pertanyaan dan membaca jawaban.
-   Menerima fallback jika informasi tidak tersedia.

### Admin/Staf Akademik

-   Login ke dashboard admin.
-   Mengelola kategori intent dan FAQ.
-   Melihat pertanyaan yang tidak terjawab.
-   Memperbarui dataset dan menjalankan pelatihan ulang bila diperlukan.

**Keputusan terbuka:** login mahasiswa belum ditentukan. MVP dapat
menyediakan chatbot tanpa login. Halaman admin wajib dilindungi
autentikasi.

## 4. Ruang Lingkup

### Termasuk MVP

-   Antarmuka chatbot web responsif.
-   Input pertanyaan Bahasa Indonesia.
-   Preprocessing teks.
-   TF-IDF dan klasifikasi intent SVM.
-   Pencarian jawaban dari basis pengetahuan.
-   Fallback untuk intent/jawaban yang tidak tersedia.
-   Login admin dan CRUD FAQ/kategori.
-   Pencatatan pertanyaan fallback.
-   Pengujian fungsional dan evaluasi model.

### Tidak termasuk MVP

-   Integrasi SIAKAD.
-   Akses nilai, IPK, pembayaran, atau data pribadi mahasiswa.
-   Pengisian KRS atau transaksi pembayaran.
-   Integrasi WhatsApp/Telegram.
-   Generative AI/LLM untuk membuat jawaban bebas.
-   Pengambilan data otomatis dari situs kampus.
-   Dukungan multi-bahasa.

## 5. Kategori Intent Awal

Kategori berikut adalah rancangan awal dan wajib disesuaikan dengan
informasi resmi kampus.

  -----------------------------------------------------------------------
  Kode                    Kategori                Contoh pertanyaan
  ----------------------- ----------------------- -----------------------
  `jadwal_kuliah`         Jadwal perkuliahan      Bagaimana cara melihat
                                                  jadwal kuliah?

  `krs`                   Kartu Rencana Studi     Kapan pengisian KRS
                                                  dibuka?

  `ukt_pembayaran`        UKT dan pembayaran      Bagaimana prosedur
                                                  pembayaran UKT?

  `kalender_akademik`     Kalender akademik       Kapan semester dimulai?

  `administrasi`          Administrasi akademik   Apa syarat surat aktif
                                                  kuliah?

  `kontak_akademik`       Kontak layanan akademik Bagaimana menghubungi
                                                  bagian akademik?

  `sapaan`                Sapaan umum             Halo, selamat pagi

  `unknown`               Tidak dikenali          Pertanyaan di luar
                                                  kategori
  -----------------------------------------------------------------------

## 6. Alur Utama Chatbot

1.  Mahasiswa membuka chatbot.
2.  Mahasiswa mengetik dan mengirim pertanyaan.
3.  Frontend mengirim pesan ke backend.
4.  Backend memvalidasi input.
5.  Sistem melakukan preprocessing.
6.  TF-IDF mengubah teks menjadi vektor.
7.  SVM memprediksi intent.
8.  Sistem memeriksa apakah prediksi cukup meyakinkan berdasarkan
    strategi threshold yang diuji.
9.  Jika dikenali, sistem mencari jawaban aktif berdasarkan intent.
10. Jika jawaban tersedia, chatbot menampilkannya.
11. Jika intent tidak dikenali atau jawaban tidak tersedia, chatbot
    menampilkan fallback.
12. Pertanyaan fallback dapat dicatat untuk ditinjau admin.

## 7. Persyaratan Fungsional

-   **FR-01 Chat UI:** menampilkan area percakapan, input, tombol kirim,
    pesan pengguna/bot, dan indikator loading.
-   **FR-02 Input:** menolak pesan kosong, membatasi panjang input,
    serta memvalidasi karakter dan payload.
-   **FR-03 Preprocessing:** minimal case folding, cleaning, tokenisasi,
    dan normalisasi jika kamus tersedia.
-   **FR-04 TF-IDF:** melakukan `fit` hanya pada data latih; gunakan
    vectorizer tersimpan yang sama saat prediksi.
-   **FR-05 SVM:** melatih dan memprediksi kategori intent. Strategi
    prediksi tidak meyakinkan harus dikonfigurasi dan diuji. Jangan
    menyebut skor keputusan sebagai probabilitas tanpa kalibrasi.
-   **FR-06 Basis pengetahuan:** setiap entri memiliki ID, intent,
    pertanyaan contoh, jawaban, sumber, status aktif, dan waktu
    pembaruan.
-   **FR-07 Jawaban:** hanya menampilkan jawaban aktif dari basis
    pengetahuan; tidak boleh mengarang kebijakan, tanggal, biaya, atau
    persyaratan.
-   **FR-08 Fallback:** menampilkan arahan ke kanal resmi jika intent
    tidak dikenal atau jawaban tidak tersedia.
-   **FR-09 Admin auth:** halaman dan endpoint admin wajib memeriksa
    autentikasi serta otorisasi; password disimpan dengan hashing.
-   **FR-10 CRUD FAQ:** admin dapat menambah, melihat, mengubah,
    menonaktifkan, dan menghapus FAQ.
-   **FR-11 Log fallback:** sistem dapat menyimpan teks pertanyaan,
    waktu, dan prediksi intent; minimalkan data pribadi.
-   **FR-12 Model versioning:** simpan model, vectorizer, metrik
    evaluasi, versi, dan tanggal pelatihan. Model baru hanya aktif
    setelah evaluasi berhasil.

## 8. Persyaratan Nonfungsional

-   **Kinerja:** target awal p95 respons maksimal 3 detik pada
    lingkungan lokal/staging; validasi melalui pengujian.
-   **Keamanan:** validasi input, proteksi SQL injection/XSS, HTTPS saat
    deployment, dan secret melalui environment variables.
-   **Usability:** responsif pada desktop dan ponsel; gunakan Bahasa
    Indonesia yang jelas.
-   **Maintainability:** pisahkan frontend, backend, pipeline NLP, dan
    basis pengetahuan.
-   **Reliability:** kegagalan model/database ditangani aman tanpa
    menampilkan stack trace atau informasi sensitif.

## 9. Arsitektur Logis

``` text
Mahasiswa
   |
Frontend Chatbot
   |
Backend API
   |
Validasi Input
   |
Text Preprocessing
   |
TF-IDF Vectorizer
   |
SVM Intent Classifier
   |
Intent dikenali?
   | Ya                  | Tidak
   v                     v
Knowledge Base         Fallback
   |
Ambil Jawaban
   |
Backend API -> Frontend -> Mahasiswa
```

Komponen pendukung: - Database: admin, intent, FAQ, dan log fallback. -
Model artifacts: model SVM, TF-IDF vectorizer, metadata versi. -
Dashboard admin: pengelolaan basis pengetahuan dan tinjauan pertanyaan
fallback.

## 10. Rancangan Data

Skema konseptual; nama tabel dan tipe data menyesuaikan stack.

### `admins`

`id`, `name`, `email`, `password_hash`, `created_at`

### `intents`

`id`, `code`, `name`, `description`, `created_at`

### `knowledge_base`

`id`, `intent_id`, `question_example`, `answer`, `source_reference`,
`is_active`, `updated_at`

### `unanswered_questions`

`id`, `question`, `predicted_intent`, `created_at`

### `model_versions`

`id`, `model_name`, `version`, `accuracy`, `f1_score`, `artifact_path`,
`trained_at`

MVP tidak memerlukan penyimpanan data pribadi atau nilai akademik
mahasiswa.

## 11. Dataset dan Pelatihan Model

Format dataset minimum:

``` csv
text,intent
"Bagaimana cara mengisi KRS?",krs
"Kapan jadwal pengisian KRS?",krs
"Bagaimana melihat jadwal kuliah?",jadwal_kuliah
"Di mana melihat kalender akademik?",kalender_akademik
"Bagaimana prosedur pembayaran UKT?",ukt_pembayaran
```

Ketentuan: - Satu baris berisi satu pertanyaan dan satu label intent. -
Sediakan variasi bahasa yang realistis untuk setiap intent. - Hindari
duplikasi yang menyebabkan kebocoran data evaluasi. - Gunakan data
resmi/relevan; data contoh harus diberi label dummy. - Pisahkan dataset
intent dari konten jawaban FAQ.

Tahapan training: 1. Memuat dan memvalidasi dataset. 2. Membersihkan
data. 3. Membagi data latih/uji secara stratified jika memungkinkan. 4.
Menjalankan preprocessing konsisten. 5. `fit` TF-IDF pada data latih. 6.
Melatih SVM. 7. Evaluasi pada data uji. 8. Simpan model, vectorizer, dan
metadata versi. 9. Uji prediksi dengan kalimat baru.

Metrik: accuracy, precision, recall, F1-score, dan confusion matrix.
Laporkan metrik per kelas jika memungkinkan. Jangan mengklaim angka
performa sebelum pengujian nyata.

## 12. Antarmuka

### Halaman chatbot

-   Nama/logo dan deskripsi.
-   Area percakapan dan pesan pembuka.
-   Contoh pertanyaan.
-   Kolom input dan tombol kirim.
-   Loading, error, dan fallback state.

### Login admin

-   Email/username, password, tombol login, dan pesan validasi.

### Dashboard admin

-   Ringkasan jumlah FAQ dan intent.
-   Menu FAQ, kategori intent, dan pertanyaan fallback.
-   Informasi versi model jika tersedia.

### Kelola FAQ

-   Daftar, pencarian, filter kategori.
-   Form tambah/edit.
-   Status aktif/nonaktif.
-   Konfirmasi penghapusan.

## 13. API Konseptual

Endpoint berikut adalah usulan, bukan endpoint yang sudah tersedia.

  Method   Endpoint                  Fungsi                Akses
  -------- ------------------------- --------------------- --------------------
  POST     `/api/chat`               Mengirim pertanyaan   Publik/mahasiswa
  POST     `/api/admin/login`        Login admin           Publik
  POST     `/api/admin/logout`       Logout                Admin
  GET      `/api/admin/faqs`         Daftar FAQ            Admin
  POST     `/api/admin/faqs`         Tambah FAQ            Admin
  PUT      `/api/admin/faqs/{id}`    Ubah FAQ              Admin
  DELETE   `/api/admin/faqs/{id}`    Hapus FAQ             Admin
  GET      `/api/admin/intents`      Daftar intent         Admin
  GET      `/api/admin/unanswered`   Daftar fallback       Admin
  GET      `/api/health`             Status aplikasi       Sesuai konfigurasi

Contoh request:

``` json
{ "message": "Bagaimana cara mengisi KRS?" }
```

Contoh response:

``` json
{
  "success": true,
  "intent": "krs",
  "answer": "Silakan lihat prosedur resmi pengisian KRS pada informasi akademik kampus.",
  "fallback": false
}
```

Response ilustratif. Jawaban produksi harus diambil dari basis
pengetahuan resmi.

## 14. Acceptance Criteria

-   **AC-01:** pesan valid yang dikirim mahasiswa diproses dan
    menghasilkan respons.
-   **AC-02:** intent yang dikenali dipetakan ke FAQ aktif yang sesuai.
-   **AC-03:** intent tidak dikenal menghasilkan fallback, bukan jawaban
    karangan.
-   **AC-04:** intent tanpa FAQ aktif menghasilkan fallback.
-   **AC-05:** input kosong ditolak dengan pesan validasi.
-   **AC-06:** admin yang login dapat menambah dan mengubah FAQ.
-   **AC-07:** pengguna tanpa hak admin ditolak dari endpoint admin.
-   **AC-08:** kegagalan model ditangani aman tanpa membocorkan detail
    internal.

## 15. Pengujian

1.  Unit test preprocessing, prediksi intent, pencarian jawaban, dan
    validasi.
2.  Integration test frontend-backend, backend-model, dan
    backend-database.
3.  Functional test alur mahasiswa dan admin.
4.  Evaluasi model menggunakan metrik klasifikasi.
5.  Usability test pada desktop dan ponsel.
6.  Security test dasar untuk autentikasi, otorisasi, dan validasi
    input.

Skenario: pertanyaan sesuai dataset, variasi ejaan, huruf kapital, input
kosong, pertanyaan di luar domain, FAQ tidak tersedia, akses admin tanpa
login, serta model/database tidak tersedia.

## 16. Tahapan Implementasi untuk AI Agent

### Tahap 1 --- Analisis repository dan persiapan

-   Periksa struktur repository, README, konfigurasi, dependency, dan
    kode.
-   Identifikasi stack yang sudah digunakan.
-   Jika repository kosong, usulkan stack dan jelaskan alasannya sebelum
    implementasi.
-   Susun struktur proyek, format dataset, dan rancangan data.

**Output:** laporan analisis, struktur proyek, dokumentasi setup,
dataset dummy.

### Tahap 2 --- Backend dan basis pengetahuan

-   Buat koneksi database dan tabel.
-   Implementasikan API chatbot.
-   Implementasikan autentikasi/otorisasi admin.
-   Tambahkan validasi dan error handling.

**Output:** backend API yang dapat diuji.

### Tahap 3 --- Pipeline NLP

-   Implementasikan preprocessing konsisten.
-   Siapkan dataset intent.
-   Implementasikan TF-IDF dan SVM.
-   Buat skrip training/evaluasi.
-   Simpan model dan vectorizer.

**Output:** artefak model, laporan evaluasi, fungsi prediksi.

### Tahap 4 --- Integrasi chatbot

-   Hubungkan API ke pipeline NLP.
-   Implementasikan pencarian jawaban dan fallback.
-   Uji alur pertanyaan sampai jawaban.

**Output:** chatbot berfungsi melalui API.

### Tahap 5 --- Frontend mahasiswa

-   Bangun UI chatbot responsif.
-   Implementasikan pesan, input, loading, dan error state.
-   Hubungkan ke API.

**Output:** antarmuka chatbot yang berfungsi.

### Tahap 6 --- Dashboard admin

-   Bangun login dan dashboard.
-   Implementasikan CRUD FAQ dan kategori.
-   Tampilkan pertanyaan fallback.
-   Uji pembatasan akses.

**Output:** admin dapat mengelola basis pengetahuan.

### Tahap 7 --- Pengujian dan dokumentasi

-   Jalankan unit, integrasi, dan functional test.
-   Evaluasi model dan perbaiki salah klasifikasi.
-   Uji fallback dan keamanan dasar.
-   Lengkapi README.

**Output:** MVP siap didemonstrasikan di lokal/staging.

## 17. Instruksi Wajib untuk AI Agent

1.  Analisis repository sebelum mengubah file.
2.  Jangan mengganti framework atau struktur yang sudah berjalan tanpa
    alasan kuat.
3.  Jangan mengarang informasi akademik. Tandai seluruh data contoh
    sebagai `DUMMY`.
4.  Pisahkan dataset training intent dan basis pengetahuan jawaban.
5.  Pastikan preprocessing training dan inference identik.
6.  Gunakan pasangan model dan vectorizer dari versi artefak yang sama.
7.  Jangan melatih model pada setiap request chat.
8.  Jangan gunakan LLM untuk mengarang jawaban pada MVP.
9.  Jangan menambahkan integrasi SIAKAD atau data pribadi tanpa
    spesifikasi dan persetujuan.
10. Simpan secret di environment variables.
11. Buat kode modular dan dapat diuji.
12. Jalankan pengujian relevan setelah setiap tahap.
13. Perbarui dokumentasi ketika cara instalasi/penggunaan berubah.
14. Jangan menambah dependency jika fungsi serupa sudah tersedia.
15. Jangan menyatakan fitur selesai sebelum diimplementasikan dan diuji.
16. Catat asumsi dan pertanyaan terbuka; jangan mengambil keputusan
    besar secara diam-diam.

### Format laporan setelah setiap tahap

-   Tujuan tahap.
-   File dibuat/diubah.
-   Fitur yang diimplementasikan.
-   Perintah menjalankan dan menguji.
-   Hasil pengujian.
-   Kendala.
-   Pekerjaan tersisa.
-   Rekomendasi tahap berikutnya.

## 18. Asumsi dan Keputusan Terbuka

  Topik                    Status
  ------------------------ ----------------------------------------------
  Framework frontend       Belum ditentukan; ikuti repository
  Framework backend        Belum ditentukan; ikuti repository
  Database                 Belum ditentukan
  Login mahasiswa          Belum ditentukan; opsional untuk MVP
  Login admin              Wajib
  Data akademik resmi      Belum tersedia; gunakan data dummy berlabel
  Threshold klasifikasi    Tentukan melalui eksperimen
  Jumlah data per intent   Belum ditentukan
  Kontak akademik resmi    Belum tersedia; jangan membuat kontak fiktif
  Hosting                  Belum ditentukan; mulai dari lokal/staging

## 19. Definition of Done

MVP selesai jika: - Mahasiswa dapat menggunakan halaman chatbot. -
Pertanyaan diproses oleh backend. - Preprocessing, TF-IDF, dan SVM
berjalan. - Intent dipetakan ke jawaban basis pengetahuan. - Fallback
berjalan saat intent/jawaban tidak tersedia. - Admin dapat login dan
mengelola FAQ. - Endpoint admin terlindungi. - Data dummy ditandai
dengan jelas. - Pengujian utama berhasil. - Dokumentasi instalasi dan
penggunaan tersedia. - Tidak ada klaim integrasi atau data resmi yang
belum diterapkan.

## 20. Instruksi Mulai

Mulai dari **Tahap 1 --- Analisis repository dan persiapan**. Periksa
teknologi, struktur folder, dan komponen yang sudah tersedia. Laporkan
hasil analisis dan usulkan rencana implementasi yang sesuai. Jangan
langsung membangun seluruh aplikasi sebelum analisis awal selesai.
