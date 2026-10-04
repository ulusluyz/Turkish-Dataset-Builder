import os
import unittest
import tempfile
import json
from dataset_cleaner.dataset.tokenizer import DefaultHeuristicTokenizer
from dataset_cleaner.dataset.splitter import chunk_text
from dataset_cleaner.dataset.sharder import ShardedJSONLWriter
from dataset_cleaner.dataset.manifest import create_manifest_and_sha256
from dataset_cleaner.reports.report import generate_reports

class TestDatasetEngine(unittest.TestCase):
    def test_tokenizer_and_splitter(self):
        tokenizer = DefaultHeuristicTokenizer()
        tokens = tokenizer.count_tokens("Merhaba dünya! Bu bir test cümlesidir.")
        self.assertGreater(tokens, 0)

        long_text = ("Bu birinci paragraftır. " * 50) + "\n\n" + ("Bu ikinci paragraftır. " * 50)
        chunks = chunk_text(long_text, max_chars=200)
        self.assertGreater(len(chunks), 1)

    def test_sharder_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            train_dir = os.path.join(tmpdir, "train")
            sharder = ShardedJSONLWriter(train_dir, prefix="train", max_docs=2)
            sharder.write({"text": "Doküman 1"})
            sharder.write({"text": "Doküman 2"})
            sharder.write({"text": "Doküman 3"})
            sharder.close()

            manifest = create_manifest_and_sha256(tmpdir, tokenizer_estimator=DefaultHeuristicTokenizer())
            self.assertEqual(len(manifest["files"]), 2)

            stats = {"processed_documents": 3, "accepted_documents": 3}
            generate_reports(tmpdir, stats, {})
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "reports", "dataset_report.json")))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "README_DATASET.md")))

if __name__ == "__main__":
    unittest.main()
