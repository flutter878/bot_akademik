from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from src.database.db import (
    get_admin_by_email,
    get_admin_by_id,
    get_all_intents,
    get_all_faqs,
    get_faq_by_id,
    create_faq,
    update_faq,
    delete_faq,
    get_unanswered_questions,
    get_dashboard_summary
)
from src.routes.auth_helpers import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.post("/login")
def login():
    """Autentikasi admin dengan email dan password."""
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    if not email or not password:
        return jsonify({
            "success": False,
            "error": "Email dan password wajib diisi."
        }), 400

    admin = get_admin_by_email(email)
    if not admin or not check_password_hash(admin["password_hash"], password):
        return jsonify({
            "success": False,
            "error": "Email atau password salah."
        }), 401

    session.clear()
    session["admin_id"] = admin["id"]
    session["admin_name"] = admin["name"]
    session["admin_email"] = admin["email"]

    return jsonify({
        "success": True,
        "message": "Login berhasil.",
        "admin": {
            "id": admin["id"],
            "name": admin["name"],
            "email": admin["email"]
        }
    })

@admin_bp.post("/logout")
def logout():
    """Keluar dari sesi admin."""
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logout berhasil."
    })

@admin_bp.get("/me")
@admin_required
def me():
    """Cek profil admin yang sedang login."""
    admin = get_admin_by_id(session["admin_id"])
    if not admin:
        session.clear()
        return jsonify({"success": False, "error": "Admin tidak ditemukan."}), 404

    return jsonify({
        "success": True,
        "admin": admin
    })

@admin_bp.get("/stats")
@admin_required
def stats():
    """Mengambil ringkasan statistik dashboard admin."""
    summary = get_dashboard_summary()
    return jsonify({
        "success": True,
        "data": summary
    })

@admin_bp.get("/intents")
@admin_required
def list_intents():
    """Mendapatkan seluruh kategori intent akademik."""
    intents = get_all_intents()
    return jsonify({
        "success": True,
        "data": intents
    })

@admin_bp.get("/faqs")
@admin_required
def list_faqs():
    """Mendapatkan daftar FAQ dengan opsi filter intent_id dan search."""
    intent_id = request.args.get("intent_id", type=int)
    search = request.args.get("search", type=str)
    active_only = request.args.get("active_only", default="false").lower() == "true"

    faqs = get_all_faqs(intent_id=intent_id, active_only=active_only, search=search)
    return jsonify({
        "success": True,
        "total": len(faqs),
        "data": faqs
    })

@admin_bp.post("/faqs")
@admin_required
def add_faq():
    """Menambahkan entri FAQ baru ke basis pengetahuan."""
    data = request.get_json(silent=True) or {}
    intent_id = data.get("intent_id")
    question_example = str(data.get("question_example", "")).strip()
    answer = str(data.get("answer", "")).strip()
    source_reference = str(data.get("source_reference", "[DUMMY] Pedoman Internal")).strip()
    is_active = 1 if data.get("is_active", True) else 0

    if not intent_id or not question_example or not answer:
        return jsonify({
            "success": False,
            "error": "Field intent_id, question_example, dan answer wajib diisi."
        }), 400

    faq_id = create_faq(
        intent_id=intent_id,
        question_example=question_example,
        answer=answer,
        source_reference=source_reference,
        is_active=is_active
    )

    return jsonify({
        "success": True,
        "message": "FAQ berhasil ditambahkan.",
        "faq_id": faq_id
    }), 201

@admin_bp.put("/faqs/<int:faq_id>")
@admin_required
def modify_faq(faq_id):
    """Mengubah entri FAQ."""
    existing = get_faq_by_id(faq_id)
    if not existing:
        return jsonify({"success": False, "error": "FAQ tidak ditemukan."}), 404

    data = request.get_json(silent=True) or {}
    intent_id = data.get("intent_id", existing["intent_id"])
    question_example = str(data.get("question_example", existing["question_example"])).strip()
    answer = str(data.get("answer", existing["answer"])).strip()
    source_reference = str(data.get("source_reference", existing["source_reference"])).strip()
    is_active = 1 if data.get("is_active", existing["is_active"]) else 0

    if not question_example or not answer:
        return jsonify({
            "success": False,
            "error": "question_example dan answer tidak boleh kosong."
        }), 400

    success = update_faq(
        faq_id=faq_id,
        intent_id=intent_id,
        question_example=question_example,
        answer=answer,
        source_reference=source_reference,
        is_active=is_active
    )

    return jsonify({
        "success": success,
        "message": "FAQ berhasil diperbarui."
    })

@admin_bp.delete("/faqs/<int:faq_id>")
@admin_required
def remove_faq(faq_id):
    """Menghapus entri FAQ."""
    existing = get_faq_by_id(faq_id)
    if not existing:
        return jsonify({"success": False, "error": "FAQ tidak ditemukan."}), 404

    success = delete_faq(faq_id)
    return jsonify({
        "success": success,
        "message": "FAQ berhasil dihapus."
    })

@admin_bp.get("/unanswered")
@admin_required
def list_unanswered():
    """Melihat log pertanyaan fallback / belum terjawab."""
    limit = request.args.get("limit", default=100, type=int)
    questions = get_unanswered_questions(limit=limit)
    return jsonify({
        "success": True,
        "total": len(questions),
        "data": questions
    })

