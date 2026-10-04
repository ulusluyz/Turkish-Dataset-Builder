import re
import hashlib
from typing import List

def get_word_ngrams(text: str, n: int = 2) -> List[str]:
    """Generates word n-grams from text (default 2 for better short-doc recall)."""
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return []
    if len(words) < n:
        return [" ".join(words)]
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]

class MinHash:
    """
    Computes MinHash signature for text using word n-grams.
    Uses num_perm hash functions with fixed seeds for reproducibility.
    """
    def __init__(self, num_perm: int = 128, seed: int = 42):
        self.num_perm = num_perm
        self.seed = seed
        self._max_hash = (1 << 32) - 1
        self._prime = 4294967311 # Large 32-bit prime
        import random
        rng = random.Random(seed)
        self._a = [rng.randint(1, self._prime - 1) for _ in range(num_perm)]
        self._b = [rng.randint(0, self._prime - 1) for _ in range(num_perm)]

    def compute_signature(self, text: str) -> List[int]:
        ngrams = get_word_ngrams(text)
        if not ngrams:
            return [0] * self.num_perm

        ngram_hashes = [int(hashlib.md5(ng.encode('utf-8')).hexdigest()[:8], 16) for ng in ngrams]

        signature = []
        for i in range(self.num_perm):
            a, b = self._a[i], self._b[i]
            min_val = min((a * h + b) % self._prime for h in ngram_hashes)
            signature.append(min_val)

        return signature
