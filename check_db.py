"""
Kiểm tra kết nối MongoDB Atlas.
Chạy trên PythonAnywhere Bash: python check_db.py
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("MONGODB_URI", "")
DB_NAME = os.getenv("MONGODB_DB_NAME", "kiemtradauvao")


def main():
    print("=== Kiem tra MongoDB ===")
    if not URI or "<db_password>" in URI:
        print("LOI: MONGODB_URI chua cau hinh hoac con placeholder <db_password>")
        sys.exit(1)

    print(f"Database: {DB_NAME}")
    print(f"URI: {URI.split('@')[-1] if '@' in URI else '(hidden)'}")

    try:
        import dns.resolver  # noqa: F401
        print("dnspython: OK")
    except ImportError:
        print("LOI: Thieu dnspython. Chay: pip install dnspython")
        sys.exit(1)

    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError

        client = MongoClient(URI, serverSelectionTimeoutMS=8000)
        client.admin.command("ping")
        db = client[DB_NAME]
        courses = db.courses.count_documents({})
        users = db.users.count_documents({})
        print("Ket noi MongoDB: THANH CONG")
        print(f"  - courses: {courses} documents")
        print(f"  - users: {users} documents")
        sys.exit(0)
    except ServerSelectionTimeoutError as e:
        err = str(e)
        print("Ket noi MongoDB: THAT BAI (ServerSelectionTimeout)")
        print()
        if "Connection refused" in err or "Errno 111" in err:
            print("Nguyen nhan: PythonAnywhere KHONG the ket noi ra MongoDB Atlas.")
            print()
            print("Giai phap:")
            print("  1. Nang cap PythonAnywhere len goi TRA PHI (Hacker $5/thang)")
            print("     -> Goi free KHONG cho phep ket noi internet ra ngoai (port 27017)")
            print("  2. MongoDB Atlas -> Network Access -> Add IP: 0.0.0.0/0")
            print("  3. Hoac deploy backend len Render/Railway (free, ket noi Atlas duoc)")
        elif "authentication failed" in err.lower():
            print("Nguyen nhan: Sai username/password trong MONGODB_URI")
        else:
            print(f"Chi tiet: {err[:500]}")
        sys.exit(1)
    except Exception as e:
        print(f"LOI khac: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
