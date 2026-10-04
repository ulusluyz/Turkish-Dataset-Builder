import re
from typing import Tuple

# Common mojibake mapping tables for Turkish characters corrupted by Latin1/Windows-1252 decoding UTF-8
MOJIBAKE_REPLACEMENTS = [
    ("Ã§", "ç"),
    ("Ã‡", "Ç"),
    ("ÄŸ", "ğ"),
    ("ÄĞ", "Ğ"),
    ("Ä±", "ı"),
    ("Ä°", "İ"),
    ("Ã¶", "ö"),
    ("Ã–", "Ö"),
    ("ÅŸ", "ş"),
    ("ÅŞ", "Ş"),
    ("Ã¼", "ü"),
    ("ÃÜ", "Ü"),
    ("â€™", "'"),
    ("â€œ", '"'),
    ("â€", '"'),
    ("Â", ""),
    ("\ufffd", ""), # replacement character REPLACEMENT CHARACTER
]

def fix_mojibake(text: str) -> Tuple[str, bool]:
    """
    Detects and fixes known Turkish mojibake patterns.
    Returns (fixed_text, was_modified).
    """
    if not text:
        return text, False

    original = text
    # Check if text contains telltale signature
    has_mojibake = any(bad in text for bad, _ in MOJIBAKE_REPLACEMENTS)

    if not has_mojibake:
        # Try byte decoding trick if common mojibake characters are found
        if "Ã" in text or "Ä" in text or "Å" in text:
            try:
                reencoded = text.encode("latin-1").decode("utf-8")
                if reencoded != text:
                    return reencoded, True
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass

    current = text
    for bad, good in MOJIBAKE_REPLACEMENTS:
        if bad in current:
            current = current.replace(bad, good)

    return current, (current != original)

def detect_unrecoverable_encoding(text: str) -> bool:
    """Returns True if document contains unrecoverable corrupted encoding markers."""
    if not text:
        return False
    # If text has excessive replacement characters or invalid null bytes
    if "\x00" in text:
        return True
    replacement_count = text.count("\ufffd")
    if replacement_count > 5 and (replacement_count / len(text)) > 0.05:
        return True
    return False
