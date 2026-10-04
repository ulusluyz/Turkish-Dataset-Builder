import unittest
import tempfile
import os
from dataset_cleaner.dedup.exact import compute_raw_hash, compute_normalized_hash, ExactDedupStore
from dataset_cleaner.dedup.near_duplicate import NearDedupStore

class TestDedup(unittest.TestCase):
    def test_exact_dedup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "exact.db")
            store = ExactDedupStore(db_path)

            doc1 = "Merhaba dünya! Bu bir test cümlesidir."
            doc2 = "  Merhaba dünya! Bu bir test cümlesidir.  "

            h1 = compute_normalized_hash(doc1)
            h2 = compute_normalized_hash(doc2)

            self.assertEqual(h1, h2)
            self.assertFalse(store.is_duplicate_and_add(h1, "doc_1"))
            self.assertTrue(store.is_duplicate_and_add(h2, "doc_2"))
            store.close()

    def test_near_dedup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "near.db")
            store = NearDedupStore(db_path, threshold=0.80)

            doc_a = "Türkiye'nin başkenti Ankara şehridir ve İç Anadolu bölgesindedir."
            doc_b = "Türkiye'nin başkenti Ankara ilidir ve İç Anadolu bölgesindedir."
            doc_c = "Fransa'nın başkenti Paris şehridir ve Avrupa kıtasındadır."

            self.assertFalse(store.is_near_duplicate_and_add(doc_a, "doc_a"))
            self.assertTrue(store.is_near_duplicate_and_add(doc_b, "doc_b"))
            self.assertFalse(store.is_near_duplicate_and_add(doc_c, "doc_c"))
            store.close()

if __name__ == "__main__":
    unittest.main()
