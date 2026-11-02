from flask import Blueprint, request, jsonify
from src.config import MAX_INPUT_LENGTH
from src.database.db import (
    get_active_faq_by_intent_code,
    log_unanswered_question
)

chat_bp = Blueprint("chat", __name__)

FALLBACK_MESSAGE = (
    "Maaf, pertanyaan Anda belum dapat saya pahami atau informasi terkait belum tersedia "
    "pada basis pengetahuan akademik saat ini. Silakan hubungi bagian Layanan Akademik kampus."
)

@chat_bp.post("/api/chat")
def handle_chat():
    """Endpoint utama pemrosesan pertanyaan mahasiswa."""
    data = request.get_json(silent=True) or {}
    # Mendukung kunci 'message' (standar PRD) maupun 'pertanyaan' (kompatibilitas backward)
    raw_message = data.get("message") or data.get("pertanyaan") or ""
    message = str(raw_message).strip()

    # Validasi Input (FR-02)
    if not message:
        return jsonify({
            "success": False,
            "error": "Pertanyaan tidak boleh kosong. Silakan ketik pertanyaan Anda."
        }), 400

    if len(message) > MAX_INPUT_LENGTH:
        return jsonify({
            "success": False,
            "error": f"Panjang pertanyaan melebihi batas maksimal ({MAX_INPUT_LENGTH} karakter)."
        }), 400

    # Cek apakah modul NLP predictor sudah tersedia (Tahap 3)
    predicted_intent = "unknown"
    confidence = 0.0
    is_fallback = True

    try:
        from src.nlp.predictor import predict_intent
        predicted_intent, confidence, is_confident = predict_intent(message)
        if is_confident and predicted_intent != "unknown":
            faq = get_active_faq_by_intent_code(predicted_intent)
            if faq:
                return jsonify({
                    "success": True,
                    "intent": predicted_intent,
                    "confidence": confidence,
                    "answer": faq["answer"],
                    "source_reference": faq.get("source_reference"),
                    "fallback": False
                })
    except ImportError:
        # Predictor belum dibuat (sedang di Tahap 2)
        pass
    except Exception as e:
        # Kegagalan runtime ditangani dengan aman tanpa membeberkan internal error
        pass

    # Jika intent tidak dikenali, tidak yakin, atau jawaban KB tidak aktif: Eksekusi Fallback
    log_unanswered_question(message, predicted_intent=predicted_intent, confidence_score=confidence)
    return jsonify({
        "success": True,
        "intent": predicted_intent,
        "confidence": confidence,
        "answer": FALLBACK_MESSAGE,
        "fallback": True
    })

@chat_bp.post("/tanya")
def legacy_tanya():
    """Rute kompatibilitas backward untuk prototipe lama."""
    res = handle_chat()
    # Jika response tuple (misal error 400), ambil respons data
    if isinstance(res, tuple):
        response_obj, status_code = res
        json_data = response_obj.get_json()
        return jsonify({"jawaban": json_data.get("error", "Terjadi kesalahan.")}), status_code
    
    json_data = res.get_json()
    return jsonify({"jawaban": json_data.get("answer")})

