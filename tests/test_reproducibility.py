import os
import unittest
import tempfile
import json
from dataset_cleaner.pipeline import ProcessingPipeline

class TestCheckpointSecurityReproducibility(unittest.TestCase):
    def test_reproducibility(self):
        with tempfile.TemporaryDirectory() as raw_dir, \
             tempfile.TemporaryDirectory() as out_dir1, \
             tempfile.TemporaryDirectory() as out_dir2:

            with open(os.path.join(raw_dir, "doc.txt"), "w", encoding="utf-8") as f:
                f.write("Türkiye'nin başkenti Ankara'dır. Ankara, İç Anadolu Bölgesi'nde yer alır. " * 5)

            config = {
                "dataset": {"train_ratio": 0.8, "validation_ratio": 0.1, "test_ratio": 0.1, "seed": 42},
                "cleaning": {"fix_mojibake": True},
                "quality": {"auto_reject_below": 40},
                "deduplication": {"enable_exact_dedup": True}
            }

            p1 = ProcessingPipeline(raw_dir, out_dir1, config)
            s1 = p1.run_build()

            p2 = ProcessingPipeline(raw_dir, out_dir2, config)
            s2 = p2.run_build()

            self.assertEqual(s1["accepted_documents"], s2["accepted_documents"])
            self.assertEqual(s1["train_documents"], s2["train_documents"])

            m1_path = os.path.join(out_dir1, "manifest", "manifest.json")
            m2_path = os.path.join(out_dir2, "manifest", "manifest.json")

            with open(m1_path, "r", encoding="utf-8") as f:
                m1 = json.load(f)
            with open(m2_path, "r", encoding="utf-8") as f:
                m2 = json.load(f)

            self.assertEqual(m1["files"][0]["sha256"], m2["files"][0]["sha256"])

    def test_input_file_immutability(self):
        with tempfile.TemporaryDirectory() as raw_dir, tempfile.TemporaryDirectory() as out_dir:
            file_path = os.path.join(raw_dir, "readonly.txt")
            content = "Bu metin kesinlikle değiştirilmemelidir!"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            mtime_before = os.path.getmtime(file_path)

            config = {"dataset": {"seed": 42}}
            pipeline = ProcessingPipeline(raw_dir, out_dir, config)
            pipeline.run_build()

            mtime_after = os.path.getmtime(file_path)
            self.assertEqual(mtime_before, mtime_after)

            with open(file_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), content)

if __name__ == "__main__":
    unittest.main()
