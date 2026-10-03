import unittest
import tempfile
import os
import json
import yaml
from dataset_cleaner.pipeline import ProcessingPipeline

class TestPipelineCLI(unittest.TestCase):
    def test_full_pipeline_run(self):
        with tempfile.TemporaryDirectory() as raw_dir, tempfile.TemporaryDirectory() as out_dir:
            # Create raw sample files
            doc1_path = os.path.join(raw_dir, "doc1.txt")
            with open(doc1_path, "w", encoding="utf-8") as f:
                f.write("Ã§ok gÃ¼zel bir gÃ¼n! Türkiye'nin başkenti Ankara'dır ve oldukça güzel bir şehirdir. " * 3)

            doc2_path = os.path.join(raw_dir, "doc2.jsonl")
            with open(doc2_path, "w", encoding="utf-8") as f:
                f.write(json.dumps({"text": "Türkiye'nin başkenti Ankara'dır ve oldukça güzel bir şehirdir. " * 3}) + "\n")
                f.write(json.dumps({"text": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}) + "\n") # Spam

            config = {
                "dataset": {"train_ratio": 0.8, "validation_ratio": 0.1, "test_ratio": 0.1, "seed": 42},
                "cleaning": {"fix_mojibake": True},
                "quality": {"auto_reject_below": 40, "review_below": 60},
                "deduplication": {"enable_exact_dedup": True, "enable_near_dedup": True}
            }

            pipeline = ProcessingPipeline(raw_dir, out_dir, config)
            stats = pipeline.run_build()

            self.assertEqual(stats["status"], "BUILD SUCCESSFUL")
            self.assertGreaterEqual(stats["accepted_documents"], 1)
            self.assertGreaterEqual(stats["rejected_documents"], 1)
            self.assertTrue(os.path.exists(os.path.join(out_dir, "manifest", "manifest.json")))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "reports", "dataset_report.json")))

if __name__ == "__main__":
    unittest.main()
