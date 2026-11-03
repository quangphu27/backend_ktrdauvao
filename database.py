from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

mongo_client = None


def mongo_uri_diagnostics(uri: str) -> dict:
    """Thông tin an toàn để debug kết nối (không lộ mật khẩu)."""
    uri = (uri or "").strip()
    info = {
        "configured": bool(uri),
        "has_placeholder": ("<db_password>" in uri) or ("YOUR_PASSWORD" in uri),
        "scheme": None,
        "user": None,
        "host": None,
        "db_in_path": None,
    }
    if not uri:
        return info
    try:
        # mongodb+srv://user:pass@host/db?...
        no_scheme = uri.split("://", 1)[-1]
        if "@" in no_scheme:
            creds, after = no_scheme.rsplit("@", 1)
            info["user"] = creds.split(":", 1)[0] if creds else None
            host_part = after.split("?", 1)[0]
            host = host_part.split("/", 1)[0]
            db = host_part.split("/", 1)[1] if "/" in host_part else None
            info["host"] = host
            info["db_in_path"] = db or None
        info["scheme"] = uri.split("://", 1)[0]
    except Exception:
        pass
    return info


def init_mongo(app):
    global mongo_client
    uri = app.config["MONGODB_URI"]
    mongo_client = MongoClient(
        uri,
        serverSelectionTimeoutMS=20000,
        connectTimeoutMS=20000,
        socketTimeoutMS=30000,
        retryWrites=True,
        tls=True,
        tlsAllowInvalidCertificates=False,
    )
    app.teardown_appcontext(close_db)


def close_db(_error=None):
    pass


def get_db():
    from flask import current_app
    return mongo_client[current_app.config["MONGODB_DB_NAME"]]


def col(name):
    return get_db()[name]


def ping_mongo():
    """Kiểm tra kết nối MongoDB."""
    try:
        mongo_client.admin.command("ping")
        return True, None
    except PyMongoError as e:
        return False, str(e)


def parse_oid(value):
    if not value:
        return None
    try:
        return ObjectId(str(value))
    except Exception:
        return None


def oid_str(value):
    return str(value) if value else None
