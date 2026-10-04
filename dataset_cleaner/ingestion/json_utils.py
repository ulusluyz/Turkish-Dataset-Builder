import uuid
from typing import Iterator, Dict, Any, Optional, List
from dataset_cleaner.ingestion.schema import RawDocument

TEXT_FIELD_CANDIDATES = [
    "text", "content", "body", "article", "document", "paragraph", "description",
    "question", "answer", "title", "input", "output", "prompt", "completion", "metin", "icerik"
]

def extract_text_from_dict(doc_dict: Dict[str, Any], specified_field: Optional[str] = None) -> tuple[Optional[str], Optional[str]]:
    """
    Extracts text string from dict.
    Returns (extracted_text, field_used).
    """
    if specified_field and specified_field in doc_dict:
        val = doc_dict[specified_field]
        if isinstance(val, str) and val.strip():
            return val, specified_field
        elif isinstance(val, (dict, list)):
            return str(val), specified_field

    for candidate in TEXT_FIELD_CANDIDATES:
        if candidate in doc_dict:
            val = doc_dict[candidate]
            if isinstance(val, str) and val.strip():
                return val, candidate

    # Fallback to question + answer if present
    if "question" in doc_dict and "answer" in doc_dict:
        q = str(doc_dict["question"]) if doc_dict["question"] else ""
        a = str(doc_dict["answer"]) if doc_dict["answer"] else ""
        combined = f"Soru: {q}\nCevap: {a}".strip()
        if combined:
            return combined, "question+answer"

    # Search any string value with length > 20
    for k, v in doc_dict.items():
        if isinstance(v, str) and len(v.strip()) > 20:
            return v, k

    return None, None
