import argparse
import sys
import os
import yaml
import uvicorn
from dataset_cleaner.pipeline import ProcessingPipeline

def load_config(config_path: str):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

def main():
    parser = argparse.ArgumentParser(description="Turkish Dataset Builder CLI")
    parser.add_argument("--input", type=str, help="Path to raw input directory or file")
    parser.add_argument("--output", type=str, help="Path to final output dataset directory")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--analyze", action="store_true", help="Run dry-run analysis mode only")
    parser.add_argument("--gui", action="store_true", help="Launch local web GUI on 127.0.0.1:8000")
    parser.add_argument("--port", type=int, default=8000, help="Port for Web GUI (default: 8000)")

    args = parser.parse_args()

    if args.gui or (not args.input and not args.output):
        print(f"Starting local Web GUI on http://127.0.0.1:{args.port} ...")
        from dataset_cleaner.app.main import app
        uvicorn.run(app, host="127.0.0.1", port=args.port)
        return

    if not args.input or not args.output:
        print("Error: Both --input and --output are required for CLI pipeline run unless --gui is specified.")
        sys.exit(1)

    config = load_config(args.config)
    pipeline = ProcessingPipeline(args.input, args.output, config)

    if args.analyze:
        print(f"Running dry-run analysis on '{args.input}'...")
        analysis = pipeline.run_analyze()
        print("\n--- ANALYSIS SUMMARY ---")
        print(f"Total Discovered Files : {analysis['total_files']}")
        print(f"Supported Files         : {analysis['supported_files']}")
        print(f"Total Size              : {analysis['total_bytes']} bytes")
        print(f"File Formats            : {analysis['file_counts']}")
        return

    print(f"Starting dataset cleaning and build from '{args.input}' to '{args.output}'...")
    stats = pipeline.run_build()
    print("\n--- BUILD SUMMARY ---")
    print(f"Status              : {stats['status']}")
    print(f"Discovered Files    : {stats['discovered_files']}")
    print(f"Processed Docs      : {stats['processed_documents']}")
    print(f"Accepted Docs       : {stats['accepted_documents']}")
    print(f"Rejected Docs       : {stats['rejected_documents']}")
    print(f"Exact Duplicates    : {stats['exact_duplicates']}")
    print(f"Near Duplicates     : {stats['near_duplicates']}")
    print(f"Train Documents     : {stats['train_documents']}")
    print(f"Val Documents       : {stats['validation_documents']}")
    print(f"Test Documents      : {stats['test_documents']}")

    if stats["status"] == "BUILD SUCCESSFUL":
        print("\n[SUCCESS] Final dataset generated and verified successfully!")
    else:
        print("\n[FAILED] Verification failed with errors:", stats.get("verification_errors", []))
        sys.exit(1)

if __name__ == "__main__":
    main()
