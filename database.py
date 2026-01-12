import sqlite3

DB_NAME = "bot.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def create_tables():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS filters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trigger TEXT UNIQUE,
        response TEXT
    )
    """)

    db.commit()
    db.close()
