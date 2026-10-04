import os
import json
import hashlib
from typing import Dict, Any, Optional

class ShardedJSONLWriter:
    """
    Streams output documents into sharded JSONL files:
    train-00000.jsonl, train-00001.jsonl, etc.
    """
    def __init__(self, output_dir: str, prefix: str = "train", max_docs: int = 100000, max_bytes: int = 104857600):
        self.output_dir = output_dir
        self.prefix = prefix
        self.max_docs = max_docs
        self.max_bytes = max_bytes
        os.makedirs(output_dir, exist_ok=True)

        self.shard_index = 0
        self.current_file_path = None
        self.current_file_handle = None
        self.current_doc_count = 0
        self.current_bytes = 0

        self.total_docs = 0
        self.total_bytes = 0
        self._open_new_shard()

    def _open_new_shard(self):
        if self.current_file_handle:
            self.current_file_handle.close()

        filename = f"{self.prefix}-{self.shard_index:05d}.jsonl"
        self.current_file_path = os.path.join(self.output_dir, filename)
        self.current_file_handle = open(self.current_file_path, "w", encoding="utf-8")
        self.current_doc_count = 0
        self.current_bytes = 0
        self.shard_index += 1

    def write(self, record: Dict[str, Any]):
        line = json.dumps(record, ensure_ascii=False) + "\n"
        line_bytes = len(line.encode("utf-8"))

        if (self.current_doc_count >= self.max_docs and self.max_docs > 0) or \
           (self.current_bytes + line_bytes >= self.max_bytes and self.max_bytes > 0):
            self._open_new_shard()

        self.current_file_handle.write(line)
        self.current_doc_count += 1
        self.current_bytes += line_bytes
        self.total_docs += 1
        self.total_bytes += line_bytes

    def close(self):
        if self.current_file_handle:
            self.current_file_handle.close()
            self.current_file_handle = None
            # If current shard was empty and not the only one, remove it
            if self.current_doc_count == 0 and self.shard_index > 1:
                try:
                    os.remove(self.current_file_path)
                except OSError:
                    pass
