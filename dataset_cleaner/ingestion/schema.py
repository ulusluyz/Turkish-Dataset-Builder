from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class RawDocument:
    doc_id: str
    source_file: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    char_count: int = 0
    line_number: Optional[int] = None
    field_used: Optional[str] = None

    def __post_init__(self):
        if not self.char_count and self.text:
            self.char_count = len(self.text)

@dataclass
class FileDiscoveryItem:
    filepath: str
    file_type: str
    size_bytes: int
    supported: bool
    skip_reason: Optional[str] = None
