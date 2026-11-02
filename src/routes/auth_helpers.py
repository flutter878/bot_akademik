from functools import wraps
from flask import session, jsonify

def admin_required(f):
    """Decorator untuk membatasi endpoint hanya bagi admin yang sudah login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_id"):
            return jsonify({
                "success": False,
                "error": "Akses ditolak. Silakan login sebagai admin terlebih dahulu."
            }), 401
        return f(*args, **kwargs)
    return decorated_function

