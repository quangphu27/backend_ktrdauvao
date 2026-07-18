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
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    @app.route("/api/health/db")
    def health_db():
        from database import ping_mongo
        ok, err = ping_mongo()
        if ok:
            return {"status": "ok", "mongodb": "connected"}
        return jsonify({
            "status": "error",
            "mongodb": "disconnected",
            "message": err,
        }), 503

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
