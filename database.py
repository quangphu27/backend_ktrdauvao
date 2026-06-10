from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

mongo_client = None


def init_mongo(app):
    global mongo_client
    uri = app.config["MONGODB_URI"]
    mongo_client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
        retryWrites=True,
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
