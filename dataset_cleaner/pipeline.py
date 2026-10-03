import os
import json
import sqlite3
import random
from typing import Dict, Any, Optional
from dataset_cleaner.ingestion.file_discovery import discover_files
from dataset_cleaner.ingestion.readers import read_document_stream
from dataset_cleaner.cleaning.text_cleaner import clean_text_pipeline
from dataset_cleaner.quality.quality_score import compute_quality_score
from dataset_cleaner.dedup.exact import ExactDedupStore, compute_normalized_hash
from dataset_cleaner.dedup.near_duplicate import NearDedupStore
from dataset_cleaner.dataset.splitter import chunk_text
from dataset_cleaner.dataset.sharder import ShardedJSONLWriter
from dataset_cleaner.dataset.tokenizer import DefaultHeuristicTokenizer
from dataset_cleaner.dataset.manifest import create_manifest_and_sha256
from dataset_cleaner.reports.report import generate_reports
from dataset_cleaner.dataset.validation import verify_final_dataset

class ProcessingPipeline:
    def __init__(self, input_dir: str, output_dir: str, config: Dict[str, Any]):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.config = config
        self.seed = config.get("dataset", {}).get("seed", 42)
        random.seed(self.seed)

        self.stats = {
            "discovered_files": 0,
            "processed_documents": 0,
            "accepted_documents": 0,
            "rejected_documents": 0,
            "exact_duplicates": 0,
            "near_duplicates": 0,
            "too_short": 0,
            "too_long": 0,
            "spam": 0,
            "non_turkish": 0,
            "train_documents": 0,
            "validation_documents": 0,
            "test_documents": 0,
            "review_queue_count": 0,
            "status": "idle",
            "progress_pct": 0.0
        }

    def run_analyze(self) -> Dict[str, Any]:
        """Runs dry-run analysis on input directory without writing output dataset."""
        discovered = list(discover_files(self.input_dir))
        file_counts = {}
        total_bytes = 0
        supported_files = 0

        for item in discovered:
            total_bytes += item.size_bytes
            file_counts[item.file_type] = file_counts.get(item.file_type, 0) + 1
            if item.supported:
                supported_files += 1

        sample_docs = []
        doc_count = 0
        for item in discovered:
            if not item.supported or doc_count >= 100:
                continue
            for doc in read_document_stream(item.filepath, item.file_type):
                doc_count += 1
                cleaned, _ = clean_text_pipeline(doc.text, file_type=item.file_type, config=self.config.get("cleaning", {}))
                score, metrics = compute_quality_score(cleaned, config=self.config.get("quality", {}))
                sample_docs.append({
                    "source": os.path.basename(doc.source_file),
                    "raw": doc.text[:200],
                    "clean": cleaned[:200],
                    "score": score,
                    "lang": metrics["lang_code"]
                })
                if len(sample_docs) >= 10:
                    break

        return {
            "total_files": len(discovered),
            "supported_files": supported_files,
            "total_bytes": total_bytes,
            "file_counts": file_counts,
            "estimated_docs": doc_count,
            "samples": sample_docs
        }

    def run_build(self) -> Dict[str, Any]:
        """Executes full reproducible dataset processing pipeline."""
        self.stats["status"] = "processing"
        os.makedirs(self.output_dir, exist_ok=True)

        # Output subdirectories
        train_dir = os.path.join(self.output_dir, "train")
        val_dir = os.path.join(self.output_dir, "validation")
        test_dir = os.path.join(self.output_dir, "test")
        rejected_dir = os.path.join(self.output_dir, "rejected")
        quarantine_dir = os.path.join(self.output_dir, "quarantine")
        review_dir = os.path.join(self.output_dir, "review")

        db_dir = os.path.join(self.output_dir, ".index")
        os.makedirs(db_dir, exist_ok=True)

        # Stores
        exact_store = ExactDedupStore(os.path.join(db_dir, "exact.db"))
        near_threshold = self.config.get("deduplication", {}).get("near_dedup_threshold", 0.80)
        near_store = NearDedupStore(os.path.join(db_dir, "near.db"), threshold=near_threshold, seed=self.seed)

        # Shard Writers
        max_docs = self.config.get("dataset", {}).get("shard_max_documents", 100000)
        max_bytes = self.config.get("dataset", {}).get("shard_max_bytes", 104857600)

        train_writer = ShardedJSONLWriter(train_dir, prefix="train", max_docs=max_docs, max_bytes=max_bytes)
        val_writer = ShardedJSONLWriter(val_dir, prefix="validation", max_docs=max_docs, max_bytes=max_bytes)
        test_writer = ShardedJSONLWriter(test_dir, prefix="test", max_docs=max_docs, max_bytes=max_bytes)

        # Rejected JSONL Writers
        os.makedirs(rejected_dir, exist_ok=True)
        rejected_handles = {
            "REJECT_TOO_SHORT": open(os.path.join(rejected_dir, "too_short.jsonl"), "a", encoding="utf-8"),
            "REJECT_DUPLICATE": open(os.path.join(rejected_dir, "duplicate.jsonl"), "a", encoding="utf-8"),
            "REJECT_NEAR_DUPLICATE": open(os.path.join(rejected_dir, "near_duplicate.jsonl"), "a", encoding="utf-8"),
            "REJECT_SPAM": open(os.path.join(rejected_dir, "spam.jsonl"), "a", encoding="utf-8"),
            "REJECT_NON_TURKISH": open(os.path.join(rejected_dir, "non_turkish.jsonl"), "a", encoding="utf-8"),
            "REJECT_INVALID_ENCODING": open(os.path.join(rejected_dir, "invalid_encoding.jsonl"), "a", encoding="utf-8"),
            "REJECT_LOW_QUALITY": open(os.path.join(rejected_dir, "invalid.jsonl"), "a", encoding="utf-8"),
        }

        # Review writer
        os.makedirs(review_dir, exist_ok=True)
        review_handle = open(os.path.join(review_dir, "review_queue.jsonl"), "a", encoding="utf-8")

        discovered = list(discover_files(self.input_dir))
        self.stats["discovered_files"] = len(discovered)

        train_ratio = self.config.get("dataset", {}).get("train_ratio", 0.98)
        val_ratio = self.config.get("dataset", {}).get("validation_ratio", 0.01)

        min_len = self.config.get("filtering", {}).get("min_character_length", 50)
        max_len = self.config.get("filtering", {}).get("max_character_length", 500000)
        should_chunk = self.config.get("filtering", {}).get("chunk_long_documents", True)

        auto_reject_below = self.config.get("quality", {}).get("auto_reject_below", 40)
        review_below = self.config.get("quality", {}).get("review_below", 60)

        for file_item in discovered:
            if not file_item.supported:
                continue

            for raw_doc in read_document_stream(file_item.filepath, file_item.file_type):
                self.stats["processed_documents"] += 1

                # Pipeline Step 1: Text Cleaning
                cleaned, clean_meta = clean_text_pipeline(raw_doc.text, file_type=file_item.file_type, config=self.config.get("cleaning", {}))

                if clean_meta.get("unrecoverable_encoding", False):
                    self.stats["rejected_documents"] += 1
                    rejected_handles["REJECT_INVALID_ENCODING"].write(json.dumps({"raw": raw_doc.text, "reason": "UNRECOVERABLE_ENCODING"}, ensure_ascii=False) + "\n")
                    continue

                # Pipeline Step 2: Chunking if long
                if len(cleaned) > max_len and should_chunk:
                    chunks = chunk_text(cleaned, max_chars=4000)
                else:
                    chunks = [cleaned]

                for chunk_txt in chunks:
                    if len(chunk_txt) < min_len:
                        self.stats["rejected_documents"] += 1
                        self.stats["too_short"] += 1
                        rejected_handles["REJECT_TOO_SHORT"].write(json.dumps({"text": chunk_txt, "reason": "TOO_SHORT"}, ensure_ascii=False) + "\n")
                        continue

                    # Pipeline Step 3: Exact Deduplication
                    norm_hash = compute_normalized_hash(chunk_txt)
                    if exact_store.is_duplicate_and_add(norm_hash, raw_doc.doc_id):
                        self.stats["rejected_documents"] += 1
                        self.stats["exact_duplicates"] += 1
                        rejected_handles["REJECT_DUPLICATE"].write(json.dumps({"text": chunk_txt, "reason": "EXACT_DUPLICATE"}, ensure_ascii=False) + "\n")
                        continue

                    # Pipeline Step 4: Near Deduplication
                    if self.config.get("deduplication", {}).get("enable_near_dedup", True):
                        if near_store.is_near_duplicate_and_add(chunk_txt, raw_doc.doc_id):
                            self.stats["rejected_documents"] += 1
                            self.stats["near_duplicates"] += 1
                            rejected_handles["REJECT_NEAR_DUPLICATE"].write(json.dumps({"text": chunk_txt, "reason": "NEAR_DUPLICATE"}, ensure_ascii=False) + "\n")
                            continue

                    # Pipeline Step 5: Quality Scoring
                    q_score, q_metrics = compute_quality_score(chunk_txt, config=self.config.get("quality", {}))

                    if q_metrics["is_spam"]:
                        self.stats["rejected_documents"] += 1
                        self.stats["spam"] += 1
                        rejected_handles["REJECT_SPAM"].write(json.dumps({"text": chunk_txt, "reason": q_metrics["spam_reason"]}, ensure_ascii=False) + "\n")
                        continue

                    if q_metrics["lang_code"] == "non_tr":
                        self.stats["rejected_documents"] += 1
                        self.stats["non_turkish"] += 1
                        rejected_handles["REJECT_NON_TURKISH"].write(json.dumps({"text": chunk_txt, "reason": "NON_TURKISH"}, ensure_ascii=False) + "\n")
                        continue

                    if q_score < auto_reject_below:
                        self.stats["rejected_documents"] += 1
                        rejected_handles["REJECT_LOW_QUALITY"].write(json.dumps({"text": chunk_txt, "score": q_score, "reason": "LOW_QUALITY_SCORE"}, ensure_ascii=False) + "\n")
                        continue

                    # Review Queue check if between auto_reject_below and review_below
                    if auto_reject_below <= q_score < review_below:
                        self.stats["review_queue_count"] += 1
                        review_handle.write(json.dumps({
                            "doc_id": raw_doc.doc_id,
                            "raw": raw_doc.text[:300],
                            "clean": chunk_txt,
                            "score": q_score
                        }, ensure_ascii=False) + "\n")

                    # Pipeline Step 6: Split Routing
                    record = {"text": chunk_txt}
                    rnd = random.random()
                    if rnd < train_ratio:
                        train_writer.write(record)
                        self.stats["train_documents"] += 1
                    elif rnd < train_ratio + val_ratio:
                        val_writer.write(record)
                        self.stats["validation_documents"] += 1
                    else:
                        test_writer.write(record)
                        self.stats["test_documents"] += 1

                    self.stats["accepted_documents"] += 1

        # Close writers & stores
        train_writer.close()
        val_writer.close()
        test_writer.close()
        exact_store.close()
        near_store.close()

        for h in rejected_handles.values():
            h.close()
        review_handle.close()

        # Step 7: Manifest & Reports Generation
        tok = DefaultHeuristicTokenizer()
        manifest_data = create_manifest_and_sha256(self.output_dir, tokenizer_estimator=tok)
        generate_reports(self.output_dir, self.stats, self.config)

        # Step 8: Final Verification Pass
        is_success, errors = verify_final_dataset(self.output_dir, manifest_data)
        if is_success:
            self.stats["status"] = "BUILD SUCCESSFUL"
        else:
            self.stats["status"] = "BUILD FAILED"
            self.stats["verification_errors"] = errors

        return self.stats
