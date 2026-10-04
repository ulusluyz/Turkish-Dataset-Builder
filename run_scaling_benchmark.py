import os
import json
import psutil
import time
import tempfile
from dataset_cleaner.pipeline import ProcessingPipeline

def run_scaling_benchmark():
    doc_counts = [1000, 2500, 5000, 10000]
    results = []

    process = psutil.Process(os.getpid())

    print("Starting Empirical Scaling RAM Benchmark...")

    for count in doc_counts:
        with tempfile.TemporaryDirectory() as raw_dir, tempfile.TemporaryDirectory() as out_dir:
            jsonl_path = os.path.join(raw_dir, "synthetic.jsonl")
            with open(jsonl_path, "w", encoding="utf-8") as f:
                for i in range(count):
                    f.write(json.dumps({
                        "id": f"doc_{i}",
                        "content": f"Doküman {i}: Elektrik enerjisi, elektrik yüklerinin hareketinden kaynaklanan bir enerji türüdür. " * 3
                    }) + "\n")

            input_size_mb = os.path.getsize(jsonl_path) / (1024 * 1024)

            initial_rss_mb = process.memory_info().rss / (1024 * 1024)
            start_time = time.time()

            config = {
                "dataset": {"shard_max_documents": 5000},
                "cleaning": {"fix_mojibake": True},
                "quality": {"auto_reject_below": 40},
                "deduplication": {"enable_exact_dedup": True, "enable_near_dedup": True}
            }

            pipeline = ProcessingPipeline(raw_dir, out_dir, config)
            stats = pipeline.run_build()

            duration = time.time() - start_time
            peak_rss_mb = process.memory_info().rss / (1024 * 1024)
            net_rss_growth = peak_rss_mb - initial_rss_mb
            throughput = count / duration if duration > 0 else 0

            res = {
                "doc_count": count,
                "input_size_mb": round(input_size_mb, 2),
                "initial_rss_mb": round(initial_rss_mb, 2),
                "peak_rss_mb": round(peak_rss_mb, 2),
                "net_rss_growth_mb": round(net_rss_growth, 2),
                "duration_sec": round(duration, 2),
                "docs_per_sec": round(throughput, 1)
            }
            results.append(res)
            print(f"Count: {count} | Size: {res['input_size_mb']} MB | Peak RSS: {res['peak_rss_mb']} MB | Growth: {res['net_rss_growth_mb']} MB | Time: {res['duration_sec']}s")

    return results

if __name__ == "__main__":
    res = run_scaling_benchmark()
    with open("reports/scaling_benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
