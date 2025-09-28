from rapidfuzz import process, fuzz
import unicodedata
import re
from typing import Optional, Tuple, Any

def normalize(s: str) -> str:
    """Basic normalization: lowercase, strip accents, remove punctuation, collapse whitespace."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

class FuzzyNameSearcher:
    def __init__(self, names: list[str]):
        """
        Initialize with a list of canonical names.
        """
        self.orig_names = names
        # Map normalized name → original name
        self.norm_to_orig = {}
        for name in names:
            nn = normalize(name)
            # If collisions, you may need to keep a list
            self.norm_to_orig[nn] = name
        self.norm_keys = list(self.norm_to_orig.keys())

    def best_match(self, query: str, threshold: float = 80.0
                   ) -> Tuple[Optional[str], float]:
        """
        Given query string, returns (best_original_name, score) if score >= threshold, else (None, score).
        """
        qn = normalize(query)
        # Use RapidFuzz’s extractOne
        res = process.extractOne(qn, self.norm_keys, scorer=fuzz.token_sort_ratio)
        if res is None:
            return None, 0.0
        norm_match, score, idx = res
        if score >= threshold:
            orig = self.norm_to_orig[norm_match]
            return orig, score
        else:
            return None, score
