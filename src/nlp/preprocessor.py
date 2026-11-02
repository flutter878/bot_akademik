import re

# Kamus normalisasi kata/singkatan umum mahasiswa Indonesia
NORMALIZATION_DICT = {
    "kpn": "kapan",
    "gmn": "bagaimana",
    "bgmn": "bagaimana",
    "gimana": "bagaimana",
    "dimana": "di mana",
    "dmn": "di mana",
    "sy": "saya",
    "aku": "saya",
    "byr": "bayar",
    "pake": "pakai",
    "pakek": "pakai",
    "bikin": "membuat",
    "buat": "membuat",
    "min": "admin",
    "adminn": "admin",
    "matkul": "mata kuliah",
    "mk": "mata kuliah",
    "spp": "ukt",
    "info": "informasi",
    "liat": "melihat",
    "cek": "melihat",
    "kalo": "kalau",
    "kl": "kalau",
    "aja": "saja",
    "wa": "whatsapp",
    "cs": "customer service",
    "no": "nomor",
    "telp": "telepon",
    "dpa": "dosen pembimbing akademik",
    "uts": "ujian tengah semester",
    "uas": "ujian akhir semester",
    "makasih": "terima kasih",
    "thx": "terima kasih",
    "tks": "terima kasih"
}

def clean_text(text: str) -> str:
    """Membersihkan karakter khusus, tanda baca, simbol berlebih, dan angka asing."""
    if not isinstance(text, str):
        return ""
    # Case folding
    text = text.lower().strip()
    # Hapus karakter non-alfanumerik kecuali spasi
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    # Hapus spasi berlebih
    text = re.sub(r"\s+", " ", text).strip()
    return text

def normalize_slang(text: str) -> str:
    """Menormalkan singkatan dan kata tidak baku berdasarkan kamus normalisasi."""
    tokens = text.split()
    normalized_tokens = [NORMALIZATION_DICT.get(token, token) for token in tokens]
    return " ".join(normalized_tokens)

def preprocess_text(text: str) -> str:
    """
    Pipeline preprocessing standar:
    1. Case folding & cleaning karakter non-alfanumerik
    2. Normalisasi kata/singkatan tidak baku
    3. Tokenisasi dan penggabungan kembali menjadi teks bersih
    """
    cleaned = clean_text(text)
    normalized = normalize_slang(cleaned)
    return normalized

