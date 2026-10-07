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
            self.client = pymongo.MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=1500,
                connectTimeoutMS=1500,
                socketTimeoutMS=1500
            )
            self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            
            # Create indexes for fast lookup
            self.db.users.create_index("username", sparse=True)
            self.db.users.create_index("unique_key", unique=True, sparse=True)
            self.db.users.create_index("email", sparse=True)
            self.db.chat_sessions.create_index("session_id", unique=True)
            self.db.chat_messages.create_index("session_id")
            self.db.raw_telemetry_logs.create_index("timestamp")
            self.db.reference_datasets.create_index("uploaded_at")
            self.db.model_retrain_history.create_index("retrained_at")
            print(f"MongoDB connected successfully to database: {DB_NAME}")
        except Exception as e:
            print(f"MongoDB connection notice ({e}). Activating embedded zero-SPOF SQLite document store...")
            self.use_fallback = True
            self._init_sqlite_fallback()

    def _init_sqlite_fallback(self):
        import sqlite3
        self.fallback_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mongo_fallback.db")
        conn = sqlite3.connect(self.fallback_db_path, timeout=20.0, check_same_thread=False)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=20000;")
        except Exception:
            pass
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                unique_key TEXT UNIQUE,
                email TEXT,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Ensure unique_key column exists if table was created in an older migration
        try:
            cursor.execute("PRAGMA table_info(users)")
            cols = [col[1] for col in cursor.fetchall()]
            if "unique_key" not in cols:
                cursor.execute("ALTER TABLE users ADD COLUMN unique_key TEXT;")
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_unique_key ON users(unique_key);")
                conn.commit()
        except Exception:
            pass
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_telemetry_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                raw_pm25 REAL NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                device_sn TEXT DEFAULT 'MOD-PM-01068',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reference_datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                record_count INTEGER NOT NULL,
                matched_count INTEGER NOT NULL,
                start_date TEXT,
                end_date TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_retrain_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                previous_r2 REAL NOT NULL,
                new_r2 REAL NOT NULL,
                previous_mae REAL NOT NULL,
                new_mae REAL NOT NULL,
                samples_used INTEGER NOT NULL,
                status TEXT NOT NULL,
                retrained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()

# Global MongoDB instance manager
mongo_mgr = MongoDBManager()

def generate_unique_string_key(prefix="AIR-US"):
    """
    Generates a secure, human-readable unique access string
    Format: AIR-US-XXXX-YYYY (e.g., AIR-US-9F8C-2A4B)
    """
    raw_hex = uuid.uuid4().hex.upper()
    return f"{prefix}-{raw_hex[:4]}-{raw_hex[4:8]}"

def _get_fallback_conn(row_factory=False):
    import sqlite3
    conn = sqlite3.connect(mongo_mgr.fallback_db_path, timeout=25.0, check_same_thread=False)
    try:
        conn.execute("PRAGMA busy_timeout=25000;")
    except Exception:
        pass
    if row_factory:
        conn.row_factory = sqlite3.Row
    return conn

# User Management Functions (Unique String Authentication & Passwordless)
def create_user_with_unique_key(username=None, custom_key=None, email=None):
    """
    Registers a new user identified by a unique string access key.
    No password required.
    """
    unique_key = (custom_key or generate_unique_string_key()).strip().upper()
    username = (username or f"Researcher-{unique_key[-4:]}").strip()
    placeholder_pw = generate_password_hash(unique_key)
    now = datetime.datetime.utcnow()

    if not mongo_mgr.use_fallback:
        try:
            user_doc = {
                "_id": str(uuid.uuid4()),
                "username": username,
                "unique_key": unique_key,
                "email": email or f"{unique_key.lower()}@airsense.local",
                "password_hash": placeholder_pw,
                "created_at": now
            }
            mongo_mgr.db.users.insert_one(user_doc)
            return {"id": user_doc["_id"], "username": username, "unique_key": unique_key, "email": user_doc["email"]}
        except pymongo.errors.DuplicateKeyError:
            return None
        except Exception as e:
            print(f"MongoDB create_user_with_unique_key fallback notice: {e}")
            mongo_mgr.use_fallback = True

    # SQLite fallback
    import sqlite3
    conn = _get_fallback_conn()
    cursor = conn.cursor()
    try:
        # Check if username exists, append suffix if so to guarantee uniqueness
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            username = f"{username} ({unique_key[-4:]})"

        cursor.execute(
            "INSERT INTO users (username, unique_key, email, password_hash) VALUES (?, ?, ?, ?)",
            (username, unique_key, email or f"{unique_key.lower()}@airsense.local", placeholder_pw)
        )
        conn.commit()
        uid = cursor.lastrowid
        conn.close()
        return {"id": str(uid), "username": username, "unique_key": unique_key, "email": email}
    except sqlite3.IntegrityError:
        conn.close()
        return None


def authenticate_user_by_unique_key(unique_key):
    """
    Authenticates a user via their unique access key string.
    """
    if not unique_key or not isinstance(unique_key, str):
        return None
    key_clean = unique_key.strip().upper()

    if not mongo_mgr.use_fallback:
        try:
            user = mongo_mgr.db.users.find_one({
                "$or": [{"unique_key": key_clean}, {"unique_key": unique_key.strip()}]
            })
            if user:
                return {
                    "id": str(user["_id"]),
                    "username": user.get("username", "Researcher"),
                    "unique_key": user.get("unique_key", key_clean),
                    "email": user.get("email")
                }
        except Exception as e:
            print(f"MongoDB authenticate_user_by_unique_key fallback notice: {e}")
            mongo_mgr.use_fallback = True

    # SQLite fallback
    import sqlite3
    conn = _get_fallback_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, unique_key, email FROM users WHERE UPPER(unique_key) = ? OR unique_key = ?", (key_clean, unique_key.strip()))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            "id": str(user["id"]),
            "username": user["username"],
            "unique_key": user["unique_key"],
            "email": user["email"]
        }
    return None


def create_user(username, email, password):
    unique_key = generate_unique_string_key()
    hashed = generate_password_hash(password)
    if not mongo_mgr.use_fallback:
        try:
            user_doc = {
                "_id": str(uuid.uuid4()),
                "username": username,
                "unique_key": unique_key,
                "email": email,
                "password_hash": hashed,
                "created_at": datetime.datetime.utcnow()
            }
            mongo_mgr.db.users.insert_one(user_doc)
            return {"id": user_doc["_id"], "username": username, "unique_key": unique_key, "email": email}
        except pymongo.errors.DuplicateKeyError:
            return None
        except Exception as e:
            print(f"MongoDB create_user fallback: {e}")
            mongo_mgr.use_fallback = True

    import sqlite3
    conn = _get_fallback_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, unique_key, email, password_hash) VALUES (?, ?, ?, ?)", (username, unique_key, email, hashed))
        conn.commit()
        uid = cursor.lastrowid
        conn.close()
        return {"id": str(uid), "username": username, "unique_key": unique_key, "email": email}
    except sqlite3.IntegrityError:
        conn.close()
        return None

def authenticate_user(username_or_email, password):
    if not mongo_mgr.use_fallback:
        try:
            user = mongo_mgr.db.users.find_one({
                "$or": [{"username": username_or_email}, {"email": username_or_email}, {"unique_key": username_or_email.upper()}]
            })
            if user and check_password_hash(user["password_hash"], password):
                return {"id": str(user["_id"]), "username": user["username"], "unique_key": user.get("unique_key"), "email": user["email"]}
            return None
        except Exception:
            mongo_mgr.use_fallback = True

    import sqlite3
    conn = _get_fallback_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ? OR UPPER(unique_key) = ?", (username_or_email, username_or_email, username_or_email.upper()))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user["password_hash"], password):
        return {"id": str(user["id"]), "username": user["username"], "unique_key": user["unique_key"], "email": user["email"]}
    return None

def get_user_by_id(user_id):
    if not mongo_mgr.use_fallback:
        try:
            user = mongo_mgr.db.users.find_one({"_id": str(user_id)})
            if user:
                return {"id": str(user["_id"]), "username": user["username"], "unique_key": user.get("unique_key"), "email": user["email"]}
            return None
        except Exception:
            mongo_mgr.use_fallback = True

    import sqlite3
    conn = _get_fallback_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, unique_key, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"id": str(user["id"]), "username": user["username"], "unique_key": user["unique_key"], "email": user["email"]}
    return None

def delete_all_user_sessions(user_id):
    """Deletes all chat sessions and messages belonging to a user."""
    if not user_id:
        return
    if not mongo_mgr.use_fallback:
        try:
            sessions = list(mongo_mgr.db.chat_sessions.find({"user_id": str(user_id)}, {"session_id": 1}))
            s_ids = [s["session_id"] for s in sessions]
            if s_ids:
                mongo_mgr.db.chat_messages.delete_many({"session_id": {"$in": s_ids}})
            mongo_mgr.db.chat_sessions.delete_many({"user_id": str(user_id)})
            return
        except Exception:
            mongo_mgr.use_fallback = True

    import sqlite3
    conn = _get_fallback_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT session_id FROM chat_sessions WHERE user_id = ?", (user_id,))
    s_ids = [r[0] for r in cursor.fetchall()]
    for sid in s_ids:
        cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (sid,))
    cursor.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Chat Session & Message Storage Functions
def get_or_create_session(session_id=None, user_id=None, title="New Conversation"):
    if not mongo_mgr.use_fallback:
        try:
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
        except Exception:
            mongo_mgr.use_fallback = True

    import sqlite3
    conn = _get_fallback_conn()
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
        try:
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
        except Exception:
            mongo_mgr.use_fallback = True

    import sqlite3
    conn = _get_fallback_conn()
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
        try:
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
            return
        except Exception:
            mongo_mgr.use_fallback = True

    import sqlite3
    conn = _get_fallback_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_messages (session_id, role, content, llm_engine, citations_json) VALUES (?, ?, ?, ?, ?)", (session_id, role, content, llm_engine, citations_json))
    cursor.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def get_session_messages(session_id):
    if not mongo_mgr.use_fallback:
        try:
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
        except Exception:
            mongo_mgr.use_fallback = True

    import sqlite3
    conn = _get_fallback_conn()
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
        conn = _get_fallback_conn()
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
        conn = _get_fallback_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

# ==============================================================================
# RAW TELEMETRY & REFERENCE MONITOR DATASET STORAGE (Continuous Learning)
# ==============================================================================
def save_raw_telemetry_batch(telemetry_records):
    """
    Ingests a list of raw telemetry dictionaries into raw_telemetry_logs collection.
    """
    if not telemetry_records:
        return 0

    now = datetime.datetime.utcnow()
    docs = []
    for r in telemetry_records:
        docs.append({
            "timestamp": str(r.get("timestamp")),
            "raw_pm25": float(r.get("raw_pm25", 0.0)),
            "temperature": float(r.get("temperature", 0.0)),
            "humidity": float(r.get("humidity", 0.0)),
            "device_sn": r.get("device_sn", "MOD-PM-01068"),
            "created_at": now
        })

    if not mongo_mgr.use_fallback:
        result = mongo_mgr.db.raw_telemetry_logs.insert_many(docs)
        return len(result.inserted_ids)
    else:
        import sqlite3
        conn = _get_fallback_conn()
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO raw_telemetry_logs (timestamp, raw_pm25, temperature, humidity, device_sn) VALUES (?, ?, ?, ?, ?)",
            [(d["timestamp"], d["raw_pm25"], d["temperature"], d["humidity"], d["device_sn"]) for d in docs]
        )
        conn.commit()
        count = cursor.rowcount
        conn.close()
        return count

def get_all_raw_telemetry():
    """
    Retrieves all raw OPC telemetry records stored in DB for matching with uploaded reference datasets.
    """
    if not mongo_mgr.use_fallback:
        cursor = mongo_mgr.db.raw_telemetry_logs.find({}, {"_id": 0}).sort("timestamp", 1)
        return list(cursor)
    else:
        import sqlite3
        conn = _get_fallback_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, raw_pm25, temperature, humidity, device_sn FROM raw_telemetry_logs ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

def save_reference_dataset_metadata(filename, record_count, matched_count, start_date, end_date):
    """
    Stores record of uploaded reference datasets.
    """
    now = datetime.datetime.utcnow()
    doc = {
        "filename": filename,
        "record_count": record_count,
        "matched_count": matched_count,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "uploaded_at": now
    }
    if not mongo_mgr.use_fallback:
        mongo_mgr.db.reference_datasets.insert_one(doc)
    else:
        import sqlite3
        conn = _get_fallback_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reference_datasets (filename, record_count, matched_count, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
            (filename, record_count, matched_count, str(start_date), str(end_date))
        )
        conn.commit()
        conn.close()

def save_model_retrain_log(model_name, previous_r2, new_r2, previous_mae, new_mae, samples_used, status):
    """
    Logs retraining events and performance progression.
    """
    now = datetime.datetime.utcnow()
    doc = {
        "model_name": model_name,
        "previous_r2": float(previous_r2),
        "new_r2": float(new_r2),
        "previous_mae": float(previous_mae),
        "new_mae": float(new_mae),
        "samples_used": int(samples_used),
        "status": status,
        "retrained_at": now
    }
    if not mongo_mgr.use_fallback:
        mongo_mgr.db.model_retrain_history.insert_one(doc)
    else:
        import sqlite3
        conn = _get_fallback_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO model_retrain_history (model_name, previous_r2, new_r2, previous_mae, new_mae, samples_used, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (model_name, previous_r2, new_r2, previous_mae, new_mae, samples_used, status)
        )
        conn.commit()
        conn.close()

def get_model_retrain_logs(limit=10):
    """
    Fetches retraining history for display in UI.
    """
    if not mongo_mgr.use_fallback:
        cursor = mongo_mgr.db.model_retrain_history.find({}, {"_id": 0}).sort("retrained_at", -1).limit(limit)
        return list(cursor)
    else:
        import sqlite3
        conn = _get_fallback_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM model_retrain_history ORDER BY retrained_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
