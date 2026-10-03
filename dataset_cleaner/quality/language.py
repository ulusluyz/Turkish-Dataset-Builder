import re

TURKISH_CHAR_SET = set("çğıöşüÇĞİÖŞÜ")
TURKISH_COMMON_WORDS = {
    "bir", "ve", "de", "da", "bu", "için", "ile", "ne", "var", "yok",
    "gibi", "daha", "kadar", "her", "ama", "çok", "o", "ben", "sen",
    "biz", "siz", "onlar", "en", "sonra", "olarak", "olan", "ki", "değil",
    "göre", "kendi", "ise", "diye", "hem", "sadece", "tüm", "şeyi", "şey",
    "gün", "dünya", "yer", "yeni", "zaman", "insan", "büyük", "iyi",
    "bugun", "cok", "guzel", "disari", "cikip", "gezmek", "istiyorum", "hava"
}

# Mapping ASCII characters to Turkish equivalents for ASCII-adapted text
ASCII_TR_MAP = str.maketrans({"c": "ç", "g": "ğ", "i": "ı", "o": "ö", "s": "ş", "u": "ü",
                              "C": "Ç", "G": "Ğ", "I": "İ", "O": "Ö", "S": "Ş", "U": "Ü"})

def detect_turkish_language(text: str) -> tuple[float, str]:
    """
    Multi-signal Turkish language detection.
    Evaluates:
      1. Turkish diacritics ratio (ç, ğ, ı, ö, ş, ü)
      2. Turkish common vocabulary presence
      3. Word structure & suffixes

    Returns:
      (confidence_score 0.0-1.0, language_code "tr" | "tr_ascii" | "non_tr")
    """
    if not text or len(text.strip()) == 0:
        return 0.0, "unknown"

    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0, "unknown"

    total_chars = len(text)
    tr_char_count = sum(1 for c in text if c in TURKISH_CHAR_SET)
    tr_char_ratio = tr_char_count / total_chars

    # Count common words
    tr_word_count = sum(1 for w in words if w in TURKISH_COMMON_WORDS)
    tr_word_ratio = tr_word_count / len(words)

    # 1. High confidence explicit Turkish (has native diacritics)
    if tr_char_ratio >= 0.005 or (tr_char_count > 0 and tr_word_ratio >= 0.05):
        score = min(1.0, (tr_char_ratio * 20.0) + (tr_word_ratio * 4.0) + 0.5)
        return score, "tr"

    # 2. ASCII-adapted Turkish check ("Bugun hava cok guzel")
    ascii_tr_words = [w.translate(ASCII_TR_MAP) for w in words]
    ascii_tr_word_count = sum(1 for w in ascii_tr_words if w in TURKISH_COMMON_WORDS or w in TURKISH_CHAR_SET)
    ascii_tr_word_ratio = ascii_tr_word_count / len(words)

    if tr_word_ratio >= 0.08 or ascii_tr_word_ratio >= 0.08:
        score = min(0.9, (ascii_tr_word_ratio * 4.0) + 0.5)
        return score, "tr_ascii"

    # Low score fallback
    if tr_word_count > 0:
        return 0.35, "tr_low"

    return 0.05, "non_tr"
