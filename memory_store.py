import sqlite3
from datetime import datetime
from pathlib import Path


class JarvisMemory:
    """Small local SQLite memory for preferences, goals, and recent interactions."""

    def __init__(self, db_path="data/jarvis_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_text TEXT NOT NULL,
                    intent TEXT,
                    confidence REAL,
                    result TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def remember(self, category, key, value):
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO memories(category, key, value, created_at) VALUES (?, ?, ?, ?)",
                (category, key, str(value), now),
            )
            conn.commit()

    def recall(self, category=None, key=None, limit=10):
        query = "SELECT category, key, value, created_at FROM memories"
        params = []
        clauses = []
        if category:
            clauses.append("category = ?")
            params.append(category)
        if key:
            clauses.append("key = ?")
            params.append(key)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {"category": r[0], "key": r[1], "value": r[2], "created_at": r[3]}
            for r in rows
        ]

    def log_interaction(self, user_text, intent, confidence, result):
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO interactions(user_text, intent, confidence, result, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_text, intent, float(confidence), str(result), now),
            )
            conn.commit()

    def recent_interactions(self, limit=10):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT user_text, intent, confidence, result, created_at
                FROM interactions ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "user_text": r[0],
                "intent": r[1],
                "confidence": r[2],
                "result": r[3],
                "created_at": r[4],
            }
            for r in rows
        ]

