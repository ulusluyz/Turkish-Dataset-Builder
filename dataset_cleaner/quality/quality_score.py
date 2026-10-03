import re
from typing import Dict, Any, Tuple
from dataset_cleaner.quality.language import detect_turkish_language
from dataset_cleaner.quality.spam import check_spam_and_junk

def compute_quality_score(
    text: str,
    config: Dict[str, Any] = None
) -> Tuple[float, Dict[str, Any]]:
    """
    Computes a transparent 0-100 quality score for a document.
    Does NOT rewrite or mutate the text.

    Metrics evaluated:
    - Turkish language confidence (0-30 pts)
    - Alphabetic character density (0-25 pts)
    - Natural sentence & whitespace layout (0-20 pts)
    - Spam / Junk penalty (-50 to 0 pts)
    - Excessive URL / digit / punctuation ratio penalty (-30 to 0 pts)
    """
    if config is None:
        config = {}

    metrics = {
        "score": 0.0,
        "char_count": len(text) if text else 0,
        "word_count": len(text.split()) if text else 0,
        "lang_confidence": 0.0,
        "lang_code": "unknown",
        "is_spam": False,
        "spam_reason": "",
        "alpha_ratio": 0.0,
        "punct_ratio": 0.0,
        "digit_ratio": 0.0,
        "url_ratio": 0.0
    }

    if not text or len(text.strip()) == 0:
        return 0.0, metrics

    total_len = len(text)
    alpha_count = sum(1 for c in text if c.isalpha())
    digit_count = sum(1 for c in text if c.isdigit())
    punct_count = sum(1 for c in text if not c.isalnum() and not c.isspace())
    urls = re.findall(r'https?://[^\s]+|www\.[^\s]+', text)
    url_chars = sum(len(u) for u in urls)

    metrics["alpha_ratio"] = alpha_count / total_len
    metrics["digit_ratio"] = digit_count / total_len
    metrics["punct_ratio"] = punct_count / total_len
    metrics["url_ratio"] = url_chars / total_len

    # 1. Language check
    lang_score, lang_code = detect_turkish_language(text)
    metrics["lang_confidence"] = lang_score
    metrics["lang_code"] = lang_code

    # 2. Spam check
    max_rep = config.get("max_repeated_char_count", 8)
    is_spam, spam_reason = check_spam_and_junk(text, max_repeated_char_count=max_rep)
    metrics["is_spam"] = is_spam
    metrics["spam_reason"] = spam_reason

    # Base score accumulation
    score = 0.0

    # Language contribution (up to 35 pts)
    score += (lang_score * 35.0)

    # Alphabetic density contribution (up to 25 pts)
    if metrics["alpha_ratio"] >= 0.60:
        score += 25.0
    else:
        score += (metrics["alpha_ratio"] / 0.60) * 25.0

    # Natural structure (sentences/words/length) (up to 25 pts)
    if metrics["word_count"] >= 10:
        score += 15.0
    else:
        score += (metrics["word_count"] / 10.0) * 15.0

    if 50 <= total_len <= 100000:
        score += 10.0

    # Penalties
    if is_spam:
        score -= 50.0

    max_punct = config.get("max_punctuation_ratio", 0.35)
    if metrics["punct_ratio"] > max_punct:
        score -= 20.0

    max_digit = config.get("max_digit_ratio", 0.40)
    if metrics["digit_ratio"] > max_digit:
        score -= 20.0

    max_url = config.get("max_url_ratio", 0.20)
    if metrics["url_ratio"] > max_url:
        score -= 25.0

    final_score = max(0.0, min(100.0, score))
    metrics["score"] = round(final_score, 2)

    return metrics["score"], metrics
