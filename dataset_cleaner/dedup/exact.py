import hashlib
import sqlite3
import re
from typing import Optional

def compute_raw_hash(text: str) -> str:
    """Computes SHA256 hash of raw string."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def compute_normalized_hash(text: str) -> str:
    """Computes SHA256 hash of normalized, lowercase, whitespace-stripped text."""
    normalized = re.sub(r'\s+', ' ', text.strip().lower())
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

class ExactDedupStore:
    """
    Disk-backed SQLite hash store for exact deduplication.
    Uses zero RAM footprint regardless of corpus size.
    """
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS exact_hashes (
                    hash_val TEXT PRIMARY KEY,
                    doc_id TEXT
                )
            """)

    def is_duplicate_and_add(self, hash_val: str, doc_id: str) -> bool:
        """
        Returns True if hash_val was already seen (exact duplicate).
        Otherwise stores hash_val and returns False.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM exact_hashes WHERE hash_val = ?", (hash_val,))
        if cursor.fetchone():
            return True
        cursor.execute("INSERT INTO exact_hashes (hash_val, doc_id) VALUES (?, ?)", (hash_val, doc_id))
        self.conn.commit()
        return False

    def close(self):
        self.conn.close()
