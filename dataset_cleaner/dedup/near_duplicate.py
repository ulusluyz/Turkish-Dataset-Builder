import sqlite3
import math
import hashlib
from typing import List, Tuple, Optional
from dataset_cleaner.dedup.fingerprint import MinHash

class NearDedupStore:
    """
    Locality-Sensitive Hashing (LSH) near-deduplication store using SQLite database.
    Bands MinHash signature into B bands of R rows.
    Uses deterministic sha256 hashing for band buckets.
    Zero-RAM growth for huge datasets.
    """
    def __init__(self, db_path: str = ":memory:", num_perm: int = 128, threshold: float = 0.80, seed: int = 42):
        self.db_path = db_path
        self.num_perm = num_perm
        self.threshold = threshold
        self.minhash = MinHash(num_perm=num_perm, seed=seed)

        self.b = 32
        self.r = num_perm // self.b
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS lsh_buckets (
                    band_id INTEGER,
                    bucket_hash TEXT,
                    doc_id TEXT,
                    PRIMARY KEY (band_id, bucket_hash, doc_id)
                )
            """)
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_lsh_lookup ON lsh_buckets (band_id, bucket_hash)
            """)

    def is_near_duplicate_and_add(self, text: str, doc_id: str) -> bool:
        signature = self.minhash.compute_signature(text)
        if not any(signature):
            return False

        cursor = self.conn.cursor()
        is_near_dup = False

        buckets_to_insert = []
        for band_idx in range(self.b):
            start = band_idx * self.r
            end = start + self.r
            band_chunk = tuple(signature[start:end])
            bucket_hash = hashlib.sha256(str(band_chunk).encode('utf-8')).hexdigest()

            if not is_near_dup:
                cursor.execute(
                    "SELECT doc_id FROM lsh_buckets WHERE band_id = ? AND bucket_hash = ? LIMIT 1",
                    (band_idx, bucket_hash)
                )
                match = cursor.fetchone()
                if match:
                    is_near_dup = True

            buckets_to_insert.append((band_idx, bucket_hash, doc_id))

        if is_near_dup:
            return True

        cursor.executemany(
            "INSERT OR IGNORE INTO lsh_buckets (band_id, bucket_hash, doc_id) VALUES (?, ?, ?)",
            buckets_to_insert
        )
        self.conn.commit()
        return False

    def close(self):
        self.conn.close()
