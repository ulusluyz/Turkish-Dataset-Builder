from abc import ABC, abstractmethod

class TokenizerInterface(ABC):
    """Abstract interface for LLM tokenizers."""

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Returns token count for the given string."""
        pass

class DefaultHeuristicTokenizer(TokenizerInterface):
    """Default heuristic token estimator (approx 1 token per 4 chars or 0.75 words)."""

    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        char_est = len(text) / 4.0
        word_est = len(text.split()) * 1.3
        return max(1, int((char_est + word_est) / 2.0))
