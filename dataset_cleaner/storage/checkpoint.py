import os
import json
import sqlite3
from typing import Set, Dict, Any

class CheckpointStore:
    """SQLite-backed checkpoint store to resume interrupted pipeline runs."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_files (
                    filepath TEXT PRIMARY KEY
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

    def is_file_processed(self, filepath: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM processed_files WHERE filepath = ?", (filepath,))
        return cursor.fetchone() is not None

    def mark_file_processed(self, filepath: str):
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO processed_files (filepath) VALUES (?)", (filepath,))

    def save_stats(self, stats: Dict[str, Any]):
        with self.conn:
            for k, v in stats.items():
                self.conn.execute("INSERT OR REPLACE INTO stats (key, value) VALUES (?, ?)", (k, json.dumps(v)))

    def load_stats(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM stats")
        res = {}
        for k, v in cursor.fetchall():
            try:
                res[k] = json.loads(v)
            except Exception:
                res[k] = v
        return res

    def close(self):
        self.conn.close()
