import os
import unittest
import tempfile
import json
import psutil
from dataset_cleaner.pipeline import ProcessingPipeline

class TestRAMBenchmark(unittest.TestCase):
    def test_ram_usage_streaming(self):
        """Generates synthetic dataset and verifies memory usage stays low and constant."""
        process = psutil.Process(os.getpid())
        initial_mem_mb = process.memory_info().rss / (1024 * 1024)

        with tempfile.TemporaryDirectory() as raw_dir, tempfile.TemporaryDirectory() as out_dir:
            # Generate 5,000 synthetic JSONL records (~5MB uncompressed)
            jsonl_path = os.path.join(raw_dir, "synthetic_large.jsonl")
            with open(jsonl_path, "w", encoding="utf-8") as f:
                for i in range(5000):
                    f.write(json.dumps({
                        "id": f"doc_{i}",
                        "content": f"Doküman {i}: Elektrik enerjisi, elektrik yüklerinin hareketinden kaynaklanan bir enerji türüdür. " * 5
                    }) + "\n")

            config = {
                "dataset": {"shard_max_documents": 1000},
                "cleaning": {"fix_mojibake": True},
                "quality": {"auto_reject_below": 40},
                "deduplication": {"enable_exact_dedup": True, "enable_near_dedup": True}
            }

            pipeline = ProcessingPipeline(raw_dir, out_dir, config)
            stats = pipeline.run_build()

            final_mem_mb = process.memory_info().rss / (1024 * 1024)
            mem_growth_mb = final_mem_mb - initial_mem_mb

            self.assertEqual(stats["status"], "BUILD SUCCESSFUL")
            self.assertEqual(stats["processed_documents"], 5000)
            # Memory growth during processing should be well bounded under 150MB
            self.assertLess(mem_growth_mb, 150.0, f"Memory grew by {mem_growth_mb:.2f} MB!")

if __name__ == "__main__":
    unittest.main()
