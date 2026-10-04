import os
from typing import Iterator, List
from dataset_cleaner.ingestion.schema import FileDiscoveryItem

SUPPORTED_EXTENSIONS = {
    ".txt": "txt",
    ".text": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".json": "json",
    ".jsonl": "jsonl",
    ".csv": "csv",
    ".tsv": "tsv",
    ".xml": "xml",
    ".html": "html",
    ".htm": "html",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".pdf": "pdf"
}

def discover_files(input_dir: str) -> Iterator[FileDiscoveryItem]:
    """Recursively walks input_dir and yields FileDiscoveryItem for all encountered files."""
    if not os.path.exists(input_dir):
        return

    if os.path.isfile(input_dir):
        ext = os.path.splitext(input_dir)[1].lower()
        file_type = SUPPORTED_EXTENSIONS.get(ext)
        size = os.path.getsize(input_dir)
        if file_type:
            yield FileDiscoveryItem(filepath=input_dir, file_type=file_type, size_bytes=size, supported=True)
        else:
            yield FileDiscoveryItem(filepath=input_dir, file_type=ext or "unknown", size_bytes=size, supported=False, skip_reason=f"Unsupported extension: '{ext}'")
        return

    for root, _, files in os.walk(input_dir):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            size = 0
            try:
                size = os.path.getsize(full_path)
            except OSError as e:
                yield FileDiscoveryItem(filepath=full_path, file_type="unknown", size_bytes=0, supported=False, skip_reason=f"Permission or OS error: {e}")
                continue

            ext = os.path.splitext(file)[1].lower()
            file_type = SUPPORTED_EXTENSIONS.get(ext)

            if file_type:
                yield FileDiscoveryItem(filepath=full_path, file_type=file_type, size_bytes=size, supported=True)
            else:
                yield FileDiscoveryItem(filepath=full_path, file_type=ext or "unknown", size_bytes=size, supported=False, skip_reason=f"Unsupported extension: '{ext}'")
