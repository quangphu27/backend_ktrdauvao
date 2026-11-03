import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from database import init_mongo
from extensions import jwt
from routes import (
    auth_bp,
    courses_bp,
    questions_bp,
    tests_bp,
    admin_bp,
    submissions_bp,
    quizzes_bp,
    classrooms_bp,
    games_bp,
    reports_bp,
    live_bp,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=False,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    init_mongo(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(tests_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(quizzes_bp)
    app.register_blueprint(classrooms_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(live_bp)

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    @app.route("/api/health/db")
    def health_db():
        from database import mongo_uri_diagnostics, ping_mongo

        diag = mongo_uri_diagnostics(app.config.get("MONGODB_URI", ""))
        diag["db_name"] = app.config.get("MONGODB_DB_NAME")

        # DNS SRV từ máy Render (hay lỗi khi thiếu dnspython / mạng DNS)
        dns_info = {"ok": False, "error": None, "targets": []}
        host = diag.get("host") or ""
        if host and "mongodb.net" in host:
            try:
                import dns.resolver

                qname = host.split("/")[0]
                if qname.startswith("cluster"):
                    qname = f"_mongodb._tcp.{qname}"
                answers = dns.resolver.resolve(qname, "SRV")
                dns_info["ok"] = True
                dns_info["targets"] = [str(r.target).rstrip(".") for r in answers]
            except Exception as e:
                dns_info["error"] = f"{type(e).__name__}: {e}"

        ok, err = ping_mongo()
        if ok:
            return {
                "status": "ok",
                "mongodb": "connected",
                "uri": diag,
                "dns": dns_info,
            }
        return jsonify({
            "status": "error",
            "mongodb": "disconnected",
            "message": err,
            "uri": diag,
            "dns": dns_info,
            "hint": (
                "Local OK nhưng Render lỗi thường do MONGODB_URI trên Render sai/thiếu. "
                "Vào Render → Environment → dán lại URI giống file .env local, rồi Manual Deploy. "
                "Atlas Network Access cần 0.0.0.0/0 Active."
            ),
        }), 503

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
