import os
import datetime
import uuid
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash

# Try loading python-dotenv
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
except Exception:
    pass

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/").strip()
DB_NAME = os.getenv("MONGO_DB_NAME", "airsense_db").strip()

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.use_fallback = False
        self._init_connection()

    def _init_connection(self):
        try:
            self.client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            # Test server connection with ping
            self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            
            # Create indexes for fast lookup
            self.db.users.create_index("username", unique=True)
            self.db.users.create_index("email", unique=True)
            self.db.chat_sessions.create_index("session_id", unique=True)
            self.db.chat_messages.create_index("session_id")
            print(f"MongoDB connected successfully to database: {DB_NAME}")
        except Exception as e:
            print(f"MongoDB server connection note ({e}). Initializing embedded document store engine...")
            self.use_fallback = True
            self._init_sqlite_fallback()

    def _init_sqlite_fallback(self):
        import sqlite3
        self.fallback_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mongo_fallback.db")
        conn = sqlite3.connect(self.fallback_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                llm_engine TEXT,
                citations_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()

# Global MongoDB instance manager
mongo_mgr = MongoDBManager()

# User Management Functions (MongoDB Schema)
def create_user(username, email, password):
    hashed = generate_password_hash(password)
    
    if not mongo_mgr.use_fallback:
        try:
            user_doc = {
                "_id": str(uuid.uuid4()),
                "username": username,
                "email": email,
                "password_hash": hashed,
                "created_at": datetime.datetime.utcnow()
            }
            mongo_mgr.db.users.insert_one(user_doc)
            return {"id": user_doc["_id"], "username": username, "email": email}
        except pymongo.errors.DuplicateKeyError:
            return None
        except Exception as e:
            print(f"MongoDB create_user error: {e}")
            return None
    else:
        import sqlite3
        conn = sqlite3.connect(mongo_mgr.fallback_db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, hashed))
            conn.commit()
            uid = cursor.lastrowid
            conn.close()
            return {"id": str(uid), "username": username, "email": email}
        except sqlite3.IntegrityError:
            conn.close()
            return None

def authenticate_user(username_or_email, password):
    if not mongo_mgr.use_fallback:
        user = mongo_mgr.db.users.find_one({
            "$or": [{"username": username_or_email}, {"email": username_or_email}]
        })
        if user and check_password_hash(user["password_hash"], password):
            return {"id": str(user["_id"]), "username": user["username"], "email": user["email"]}
        return None
    else:
        import sqlite3
        conn = sqlite3.connect(mongo_mgr.fallback_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username_or_email, username_or_email))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            return {"id": str(user["id"]), "username": user["username"], "email": user["email"]}
        return None

def get_user_by_id(user_id):
    if not mongo_mgr.use_fallback:
        user = mongo_mgr.db.users.find_one({"_id": str(user_id)})
        if user:
            return {"id": str(user["_id"]), "username": user["username"], "email": user["email"]}
        return None
    else:
        import sqlite3
        conn = sqlite3.connect(mongo_mgr.fallback_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return {"id": str(user["id"]), "username": user["username"], "email": user["email"]}
        return None

# Chat Session & Message Storage Functions (MongoDB BSON Documents)
def get_or_create_session(session_id=None, user_id=None, title="New Conversation"):
    if not mongo_mgr.use_fallback:
        if session_id:
            session = mongo_mgr.db.chat_sessions.find_one({"session_id": session_id})
            if session:
                return {
                    "session_id": session["session_id"],
                    "user_id": session.get("user_id"),
                    "title": session.get("title", title),
                    "updated_at": session.get("updated_at", "")
                }
        
        new_id = session_id or str(uuid.uuid4())
        session_doc = {
            "session_id": new_id,
            "user_id": str(user_id) if user_id else None,
            "title": title,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        mongo_mgr.db.chat_sessions.insert_one(session_doc)
        return {
            "session_id": new_id,
            "user_id": str(user_id) if user_id else None,
            "title": title
        }
    else:
        import sqlite3
        conn = sqlite3.connect(mongo_mgr.fallback_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if session_id:
            cursor.execute("SELECT * FROM chat_sessions WHERE session_id = ?", (session_id,))
            sess = cursor.fetchone()
            if sess:
                conn.close()
                return dict(sess)
        
        new_id = session_id or str(uuid.uuid4())
        cursor.execute("INSERT INTO chat_sessions (session_id, user_id, title) VALUES (?, ?, ?)", (new_id, user_id, title))
        conn.commit()
        conn.close()
        return {"session_id": new_id, "user_id": user_id, "title": title}

def list_user_sessions(user_id=None, limit=20):
    if not mongo_mgr.use_fallback:
        query = {"user_id": str(user_id)} if user_id else {"user_id": None}
        cursor = mongo_mgr.db.chat_sessions.find(query).sort("updated_at", -1).limit(limit)
        results = []
        for s in cursor:
            results.append({
                "session_id": s["session_id"],
                "user_id": s.get("user_id"),
                "title": s.get("title", "Conversation"),
                "updated_at": str(s.get("updated_at", ""))
            })
        return results
    else:
        import sqlite3
        conn = sqlite3.connect(mongo_mgr.fallback_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?", (user_id, limit))
        else:
            cursor.execute("SELECT * FROM chat_sessions WHERE user_id IS NULL ORDER BY updated_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

def add_chat_message(session_id, role, content, llm_engine=None, citations_json=None):
    now = datetime.datetime.utcnow()
    if not mongo_mgr.use_fallback:
        msg_doc = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "llm_engine": llm_engine,
            "citations_json": citations_json,
            "created_at": now
        }
        mongo_mgr.db.chat_messages.insert_one(msg_doc)
        mongo_mgr.db.chat_sessions.update_one(
            {"session_id": session_id},
            {"$set": {"updated_at": now}}
        )
    else:
        import sqlite3
        conn = sqlite3.connect(mongo_mgr.fallback_db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_messages (session_id, role, content, llm_engine, citations_json) VALUES (?, ?, ?, ?, ?)", (session_id, role, content, llm_engine, citations_json))
        cursor.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

def get_session_messages(session_id):
    if not mongo_mgr.use_fallback:
        cursor = mongo_mgr.db.chat_messages.find({"session_id": session_id}).sort("created_at", 1)
        results = []
        for m in cursor:
            results.append({
                "role": m["role"],
                "content": m["content"],
                "llm_engine": m.get("llm_engine"),
                "citations_json": m.get("citations_json"),
                "created_at": str(m.get("created_at", ""))
            })
        return results
    else:
        import sqlite3
        conn = sqlite3.connect(mongo_mgr.fallback_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT role, content, llm_engine, citations_json, created_at FROM chat_messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

def update_session_title(session_id, title):
    if not mongo_mgr.use_fallback:
        mongo_mgr.db.chat_sessions.update_one(
            {"session_id": session_id},
            {"$set": {"title": title[:60]}}
        )
    else:
        import sqlite3
        conn = sqlite3.connect(mongo_mgr.fallback_db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE chat_sessions SET title = ? WHERE session_id = ?", (title[:60], session_id))
        conn.commit()
        conn.close()

def delete_session(session_id):
    if not mongo_mgr.use_fallback:
        mongo_mgr.db.chat_messages.delete_many({"session_id": session_id})
        mongo_mgr.db.chat_sessions.delete_one({"session_id": session_id})
    else:
        import sqlite3
        conn = sqlite3.connect(mongo_mgr.fallback_db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
