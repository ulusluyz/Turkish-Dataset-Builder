import re
import unicodedata

# Non-printable control characters excluding newline, carriage return, tab
CONTROL_CHAR_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')

def normalize_unicode(text: str, form: str = "NFC") -> str:
    """Applies Unicode normalization (default NFC)."""
    if not text:
        return ""
    # Strip Byte Order Mark if present
    if text.startswith('\ufeff'):
        text = text[1:]
    return unicodedata.normalize(form, text)

def remove_control_characters(text: str) -> str:
    """Removes invisible control characters while preserving standard whitespaces."""
    if not text:
        return ""
    return CONTROL_CHAR_RE.sub('', text)
