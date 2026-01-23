# database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing")


def get_db():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        cursor_factory=RealDictCursor
    )


def create_tables():
    db = get_db()
    cur = db.cursor()

    # 🔹 sponsor / filtre tablosu (ESKİ – DOKUNULMADI)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS filters (
        trigger TEXT PRIMARY KEY,
        response TEXT NOT NULL
    );
    """)

    # 🔹 mesaj sayacı tablosu (YENİ)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS message_stats (
        chat_id BIGINT NOT NULL,
        user_id BIGINT NOT NULL,
        message_count INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (chat_id, user_id)
    );
    """)

    db.commit()
    cur.close()
    db.close()
