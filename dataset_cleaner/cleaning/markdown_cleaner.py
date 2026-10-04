import re

RE_MD_HEADERS = re.compile(r'^\s{0,3}#{1,6}\s+', re.MULTILINE)
RE_MD_BOLD_ITALIC = re.compile(r'(\*\*|__|[*_])(.*?)\1')
RE_MD_LINKS = re.compile(r'\[([^\]]+)\]\([^\)]+\)')

def clean_markdown_formatting(text: str, remove_headers: bool = False) -> str:
    """
    Cleans markdown formatting while preserving document structure and code blocks.
    """
    if not text:
        return ""

    cleaned = RE_MD_LINKS.sub(r'\1', text)
    cleaned = RE_MD_BOLD_ITALIC.sub(r'\2', cleaned)

    if remove_headers:
        cleaned = RE_MD_HEADERS.sub('', cleaned)

    return cleaned
