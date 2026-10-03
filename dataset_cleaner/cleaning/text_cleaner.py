from typing import Tuple, Dict, Any
from dataset_cleaner.cleaning.encoding import fix_mojibake, detect_unrecoverable_encoding
from dataset_cleaner.cleaning.unicode import normalize_unicode, remove_control_characters
from dataset_cleaner.cleaning.whitespace import normalize_whitespace, unescape_entities
from dataset_cleaner.cleaning.html_cleaner import clean_html_content
from dataset_cleaner.cleaning.markdown_cleaner import clean_markdown_formatting

def clean_text_pipeline(
    text: str,
    file_type: str = "txt",
    config: Dict[str, Any] = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Applies the full cleaning pipeline deterministically.
    Returns (cleaned_text, cleaning_metadata).
    """
    if config is None:
        config = {}

    meta = {
        "mojibake_fixed": False,
        "unrecoverable_encoding": False,
        "original_len": len(text) if text else 0,
        "cleaned_len": 0
    }

    if not text:
        return "", meta

    current = text

    # Check unrecoverable encoding
    if detect_unrecoverable_encoding(current):
        meta["unrecoverable_encoding"] = True

    # 1. Mojibake fixing
    if config.get("fix_mojibake", True):
        current, was_fixed = fix_mojibake(current)
        if was_fixed:
            meta["mojibake_fixed"] = True

    # 2. Control characters & Unicode normalization
    if config.get("remove_control_characters", True):
        current = remove_control_characters(current)

    if config.get("normalize_unicode", True):
        form = config.get("unicode_form", "NFC")
        current = normalize_unicode(current, form=form)

    # 3. HTML / HTML Entity cleaning
    if file_type == "html" or config.get("clean_html", True):
        current = clean_html_content(current)

    if config.get("unescape_html_entities", True):
        current = unescape_entities(current)

    # 4. Markdown cleaning (if file is markdown or config enabled)
    if file_type == "markdown" and config.get("clean_markdown_wrapping", False):
        current = clean_markdown_formatting(current)

    # 5. Whitespace normalization
    if config.get("normalize_whitespace", True):
        current = normalize_whitespace(current)

    meta["cleaned_len"] = len(current)
    return current, meta
