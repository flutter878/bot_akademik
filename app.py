import os
from flask import Flask, render_template, jsonify, session, redirect, url_for
from src.config import SECRET_KEY, DB_PATH
from src.database.db import init_db, seed_default_data
from src.routes.chat import chat_bp
from src.routes.admin import admin_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    if test_config:
        app.config.update(test_config)

    # Inisialisasi Database dan Seed Data jika belum ada
    if not test_config or test_config.get("INIT_DB", True):
        init_db(app.config.get("DB_PATH", DB_PATH))
        seed_default_data(app.config.get("DB_PATH", DB_PATH))

    # Daftarkan Blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/admin")
    def admin_page():
        if "admin_id" not in session:
            return redirect(url_for("admin_login_page"))
        return render_template("admin_dashboard.html")

    @app.route("/admin/login")
    def admin_login_page():
        if "admin_id" in session:
            return redirect(url_for("admin_page"))
        return render_template("admin_login.html")

    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "healthy",
            "database": "connected" if os.path.exists(DB_PATH) else "not_found"
        })

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
