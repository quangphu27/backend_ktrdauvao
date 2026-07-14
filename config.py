import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    MONGODB_URI = os.getenv(
        "MONGODB_URI",
        "mongodb+srv://quangphu:<db_password>@cluster0.6ln3p.mongodb.net/?appName=Cluster0",
    )
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "kiemtradauvao")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://kiemtradauvao.vercel.app").rstrip("/")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_SUBMISSION_EXTENSIONS = {
        "sb3", "sb2", "png", "jpg", "jpeg", "gif", "webp", "pdf", "zip", "txt", "doc", "docx",
    }
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "dnqrhfnas")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY") or os.getenv("API-KEY") or os.getenv("API_KEY")
    CLOUDINARY_API_SECRET = (
        os.getenv("CLOUDINARY_API_SECRET") or os.getenv("API-SECRET") or os.getenv("API_SECRET")
    )
    CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
