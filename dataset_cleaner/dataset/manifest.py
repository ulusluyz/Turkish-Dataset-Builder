import os
import json
import hashlib
from typing import Dict, Any, List

def compute_file_sha256(filepath: str) -> str:
    """Computes SHA256 hex digest of file in streaming chunks."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def create_manifest_and_sha256(
    final_dir: str,
    tokenizer_estimator=None
) -> Dict[str, Any]:
    """
    Scans generated dataset shards in train/, validation/, test/, rejected/, quarantine/
    and creates manifest/manifest.json and manifest/SHA256SUMS.
    """
    manifest_dir = os.path.join(final_dir, "manifest")
    os.makedirs(manifest_dir, exist_ok=True)

    file_entries = []
    sha256_lines = []

    subdirs = ["train", "validation", "test", "rejected", "quarantine"]
    for sub in subdirs:
        subpath = os.path.join(final_dir, sub)
        if not os.path.exists(subpath):
            continue

        for root, _, files in os.walk(subpath):
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                rel_path = os.path.relpath(fpath, final_dir)
                size_bytes = os.path.getsize(fpath)
                sha256_hash = compute_file_sha256(fpath)

                doc_count = 0
                char_count = 0
                word_count = 0
                est_tokens = 0

                if fname.endswith(".jsonl"):
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        for line in f:
                            line_str = line.strip()
                            if not line_str:
                                continue
                            try:
                                data = json.loads(line_str)
                                text = data.get("text", "")
                                doc_count += 1
                                char_count += len(text)
                                word_count += len(text.split())
                                if tokenizer_estimator:
                                    est_tokens += tokenizer_estimator.count_tokens(text)
                            except Exception:
                                pass

                entry = {
                    "filepath": rel_path,
                    "size_bytes": size_bytes,
                    "sha256": sha256_hash,
                    "document_count": doc_count,
                    "character_count": char_count,
                    "word_count": word_count,
                    "estimated_token_count": est_tokens
                }
                file_entries.append(entry)
                sha256_lines.append(f"{sha256_hash}  {rel_path}\n")

    manifest_data = {
        "dataset_version": "1.0",
        "files": file_entries
    }

    with open(os.path.join(manifest_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    with open(os.path.join(manifest_dir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.writelines(sha256_lines)

    return manifest_data
