import os
import unittest
import tempfile
import json
from dataset_cleaner.dataset.validation import verify_final_dataset

class TestValidationPass(unittest.TestCase):
    def test_verify_final_dataset_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            train_dir = os.path.join(tmpdir, "train")
            os.makedirs(train_dir, exist_ok=True)
            fpath = os.path.join(train_dir, "train-00000.jsonl")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(json.dumps({"text": "Valid document"}) + "\n")

            import hashlib
            sha = hashlib.sha256(open(fpath, "rb").read()).hexdigest()
            manifest_data = {
                "files": [
                    {"filepath": "train/train-00000.jsonl", "sha256": sha}
                ]
            }

            success, errors = verify_final_dataset(tmpdir, manifest_data)
            self.assertTrue(success)
            self.assertEqual(len(errors), 0)

if __name__ == "__main__":
    unittest.main()
