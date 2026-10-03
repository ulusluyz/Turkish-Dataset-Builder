import re

RE_URL = re.compile(r'https?://[^\s]+|www\.[^\s]+')
RE_REPEATED_CHARS = re.compile(r'(.)\1{7,}') # e.g. aaaaaaaa
RE_KEYBOARD_MASH = re.compile(r'^[asdfghjklñzxcvbnmşiğüöç1234567890]+$', re.IGNORECASE)

SPAM_KEYWORDS = {
    "bahis", "casino", "poker", "slot", "kaçak iddaa", "bonus veritabanı",
    "kredi kartı borcu", "şans oyunları", "tıkla indir", "whatsapp grubu",
    "canlı maç izle", "bedava izle", "escort", "sohbet hattı"
}

def check_spam_and_junk(text: str, max_repeated_char_count: int = 8) -> tuple[bool, str]:
    """
    Checks if text is spam, OCR garbage, or keyboard mashing.
    Returns (is_spam, reason).
    """
    if not text:
        return True, "EMPTY"

    stripped = text.strip()
    if len(stripped) == 0:
        return True, "EMPTY"

    # Check repeated characters e.g. aaaaaaaaaaaa
    if re.search(r'(.)\1{' + str(max_repeated_char_count) + r',}', text):
        return True, "REPEATED_CHARACTERS"

    # Check keyboard mash e.g. asdfghjkl
    if len(stripped) < 50 and RE_KEYBOARD_MASH.match(stripped) and " " not in stripped:
        return True, "KEYBOARD_MASH"

    # Check single word repeating e.g. "test test test test test"
    words = stripped.lower().split()
    if len(words) > 10 and len(set(words)) <= 2:
        return True, "REPEATED_WORD_SPAM"

    # Check explicit spam keywords
    text_lower = text.lower()
    spam_matches = sum(1 for kw in SPAM_KEYWORDS if kw in text_lower)
    if spam_matches >= 2:
        return True, "SPAM_KEYWORDS"

    # Check if text is purely punctuation or numbers or URLs
    alpha_chars = sum(1 for c in text if c.isalpha())
    if alpha_chars == 0 and len(text) > 10:
        return True, "NO_ALPHABETIC_CHARACTERS"

    return False, ""
