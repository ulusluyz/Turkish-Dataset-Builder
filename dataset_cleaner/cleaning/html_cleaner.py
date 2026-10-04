import re
from html.parser import HTMLParser

RE_SCRIPT_STYLE = re.compile(r'<(script|style|svg|noscript|iframe)[^>]*>.*?</\1>', re.DOTALL | re.IGNORECASE)
RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_COOKIES_REKLAM = re.compile(
    r'(çerez politikası|cookie policy|tüm hakları saklıdır|copyright \d{4}|tıkla ve başla|abone ol|paylaş|sosyal medya|daha fazla bilgi için|giriş yap|kayıt ol)',
    re.IGNORECASE
)

def clean_html_content(text: str) -> str:
    """Strips script/style blocks, HTML tags, and converts breaks to linebreaks."""
    if not text:
        return ""

    if '<' not in text or '>' not in text:
        return text

    # Remove scripts, styles, SVG
    cleaned = RE_SCRIPT_STYLE.sub(' ', text)

    # Convert common HTML line break elements to actual line breaks
    cleaned = re.sub(r'<(br|p|div|tr|h[1-6])\b[^>]*>', '\n', cleaned, flags=re.IGNORECASE)

    # Strip remaining HTML tags
    cleaned = RE_HTML_TAGS.sub(' ', cleaned)

    return cleaned
