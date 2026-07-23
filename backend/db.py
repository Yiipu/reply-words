import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'community.db')
COMMUNITY_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'community.json')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('leader', 'colleague')),
            mode TEXT NOT NULL CHECK(mode IN ('ok', 'no')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            vote INTEGER NOT NULL CHECK(vote IN (1, -1)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (word_id) REFERENCES words(id)
        );
        CREATE INDEX IF NOT EXISTS idx_feedback_word ON feedback(word_id);
        CREATE INDEX IF NOT EXISTS idx_words_active ON words(active);
    """)
    conn.commit()
    conn.close()

def add_word(text, category, mode):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO words (text, category, mode) VALUES (?, ?, ?)",
        (text, category, mode)
    )
    word_id = cur.lastrowid
    conn.commit()
    conn.close()
    rebuild_community_json()
    return word_id

def add_feedback(word_id, vote):
    conn = get_db()
    conn.execute(
        "INSERT INTO feedback (word_id, vote) VALUES (?, ?)",
        (word_id, vote)
    )
    conn.commit()
    conn.close()

def word_exists(text, category, mode):
    conn = get_db()
    row = conn.execute(
        "SELECT id FROM words WHERE text=? AND category=? AND mode=? AND active=1",
        (text, category, mode)
    ).fetchone()
    conn.close()
    return row is not None

def get_community_words():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, text, category, mode FROM words WHERE active=1 ORDER BY id"
    ).fetchall()
    conn.close()
    result = {"ok": {"leader": [], "colleague": []}, "no": {"leader": [], "colleague": []}}
    for row in rows:
        result[row["mode"]][row["category"]].append({"id": row["id"], "text": row["text"]})
    return result

def rebuild_community_json():
    data = get_community_words()
    with open(COMMUNITY_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def run_fade_out():
    conn = get_db()
    rows = conn.execute("""
        SELECT w.id,
               SUM(CASE WHEN f.vote=1 THEN 1 ELSE 0 END) as pos,
               SUM(CASE WHEN f.vote=-1 THEN 1 ELSE 0 END) as neg
        FROM words w
        LEFT JOIN feedback f ON f.word_id = w.id
        WHERE w.active = 1
        GROUP BY w.id
        HAVING neg > pos * 1.5
    """).fetchall()
    faded = 0
    for row in rows:
        conn.execute("UPDATE words SET active=0 WHERE id=?", (row["id"],))
        faded += 1
    conn.commit()
    conn.close()
    if faded > 0:
        rebuild_community_json()
    return faded

init_db()
