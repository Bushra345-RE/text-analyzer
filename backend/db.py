import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, text TEXT NOT NULL, result TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")


def save(title, text, result):
    with conn() as c:
        return c.execute("INSERT INTO analyses (title, text, result) VALUES (?,?,?)",
                         (title, text, json.dumps(result))).lastrowid


def history():
    with conn() as c:
        rows = c.execute("SELECT id, title, substr(text,1,110) AS preview, result, created_at "
                         "FROM analyses ORDER BY id DESC LIMIT 30").fetchall()
    out = []
    for r in rows:
        res = json.loads(r["result"])
        out.append({"id": r["id"], "title": r["title"], "preview": r["preview"],
                    "created_at": r["created_at"], "words": res["stats"]["words"],
                    "sentiment": res["sentiment"]["label"]})
    return out


def get(i):
    with conn() as c:
        r = c.execute("SELECT * FROM analyses WHERE id=?", (i,)).fetchone()
    if not r:
        return None
    return {"id": r["id"], "title": r["title"], "text": r["text"], "result": json.loads(r["result"])}


def delete(i):
    with conn() as c:
        c.execute("DELETE FROM analyses WHERE id=?", (i,))
