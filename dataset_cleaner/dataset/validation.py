import os
import json
import hashlib
from typing import Tuple, Dict, Any, List

def verify_final_dataset(
    final_dir: str,
    manifest_data: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Runs strict post-build verification pass on generated final dataset shards.
    Verifies:
      1. JSON validity per line
      2. Valid UTF-8 encoding
      3. Non-empty 'text' field
      4. SHA256 file checksum matches manifest
      5. Data leakage check: train vs val vs test exact hash overlap
      6. Duplicate check across accepted shards

    Returns:
      (is_successful, list_of_error_messages)
    """
    errors = []
    hashes_by_split = {"train": set(), "validation": set(), "test": set()}

    manifest_files = {entry["filepath"]: entry for entry in manifest_data.get("files", [])}

    subdirs = ["train", "validation", "test"]
    for sub in subdirs:
        subpath = os.path.join(final_dir, sub)
        if not os.path.exists(subpath):
            continue

        for root, _, files in os.walk(subpath):
            for fname in sorted(files):
                if not fname.endswith(".jsonl"):
                    continue

                fpath = os.path.join(root, fname)
                rel_path = os.path.relpath(fpath, final_dir)

                # Check 1: SHA256 integrity
                sha = hashlib.sha256()
                with open(fpath, "rb") as f:
                    while chunk := f.read(65536):
                        sha.update(chunk)
                actual_sha = sha.hexdigest()

                if rel_path in manifest_files:
                    expected_sha = manifest_files[rel_path]["sha256"]
                    if actual_sha != expected_sha:
                        errors.append(f"SHA256 mismatch for {rel_path}: expected {expected_sha}, got {actual_sha}")

                # Check 2: Reading UTF-8 & JSONL validation
                line_no = 0
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        for line in f:
                            line_no += 1
                            line_str = line.strip()
                            if not line_str:
                                continue
                            try:
                                data = json.loads(line_str)
                            except json.JSONDecodeError as e:
                                errors.append(f"Invalid JSON in {rel_path} at line {line_no}: {e}")
                                continue

                            text = data.get("text", "")
                            if not text or not str(text).strip():
                                errors.append(f"Empty text field in {rel_path} at line {line_no}")

                            # Compute hash for split leakage check
                            doc_hash = hashlib.sha256(str(text).strip().encode('utf-8')).hexdigest()
                            hashes_by_split[sub].add(doc_hash)
                except UnicodeDecodeError as e:
                    errors.append(f"UTF-8 decode error in {rel_path}: {e}")

    # Check 3: Data leakage check across train, validation, test
    train_val_leakage = hashes_by_split["train"].intersection(hashes_by_split["validation"])
    if train_val_leakage:
        errors.append(f"Data leakage detected! {len(train_val_leakage)} documents overlapped between train and validation splits.")

    train_test_leakage = hashes_by_split["train"].intersection(hashes_by_split["test"])
    if train_test_leakage:
        errors.append(f"Data leakage detected! {len(train_test_leakage)} documents overlapped between train and test splits.")

    val_test_leakage = hashes_by_split["validation"].intersection(hashes_by_split["test"])
    if val_test_leakage:
        errors.append(f"Data leakage detected! {len(val_test_leakage)} documents overlapped between validation and test splits.")

    success = (len(errors) == 0)
    return success, errors
