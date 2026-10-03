import re
import html

RE_MULTIPLE_SPACES = re.compile(r'[ \t]+')
RE_MULTIPLE_NEWLINES = re.compile(r'\n{3,}')
RE_URL_AROUND_SPACES = re.compile(r'(https?://[^\s]+)')

def normalize_whitespace(text: str) -> str:
    """
    Standardizes whitespace, line breaks (\r\n -> \n), trailing spaces,
    and collapses excessive blank lines (> 2 newlines).
    """
    if not text:
        return ""

    # Normalize line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Trim spaces per line
    lines = [RE_MULTIPLE_SPACES.sub(' ', line).strip() for line in text.split('\n')]

    joined = '\n'.join(lines)
    # Collapse 3+ newlines into 2
    joined = RE_MULTIPLE_NEWLINES.sub('\n\n', joined)

    return joined.strip()

def unescape_entities(text: str) -> str:
    """Unescapes HTML entities e.g., &amp; -> &."""
    if not text or '&' not in text:
        return text
    return html.unescape(text)
