import json
import sqlite3

JSON_FILE = "sponsorlar.json"
DB_FILE = "bot.db"

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

db = sqlite3.connect(DB_FILE)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger TEXT UNIQUE,
    response TEXT
)
""")

sayac = 0
for trigger, response in data.items():
    cur.execute(
        "INSERT OR REPLACE INTO filters (trigger, response) VALUES (?, ?)",
        (trigger.lower(), response)
    )
    sayac += 1

db.commit()
db.close()

print(f"✅ {sayac} kayıt SQLite'a aktarıldı")
