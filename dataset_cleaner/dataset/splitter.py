import re
from typing import List

def chunk_text(
    text: str,
    max_chars: int = 4000,
    overlap_chars: int = 200
) -> List[str]:
    """
    Splits long text into chunks preserving sentence and paragraph boundaries.
    Never cuts in the middle of a word.
    """
    if not text or len(text) <= max_chars:
        return [text] if text else []

    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len + 2 <= max_chars:
            current_chunk.append(para)
            current_len += para_len + 2
        else:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))

            # If para itself exceeds max_chars, split by sentences
            if para_len > max_chars:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                sent_chunk = []
                sent_len = 0
                for sent in sentences:
                    if sent_len + len(sent) + 1 <= max_chars:
                        sent_chunk.append(sent)
                        sent_len += len(sent) + 1
                    else:
                        if sent_chunk:
                            chunks.append(' '.join(sent_chunk))
                        sent_chunk = [sent]
                        sent_len = len(sent)
                if sent_chunk:
                    chunks.append(' '.join(sent_chunk))
                current_chunk = []
                current_len = 0
            else:
                current_chunk = [para]
                current_len = para_len

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks
