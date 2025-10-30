import re
from typing import List


_token_re = re.compile(r"\w+|\s+|[^\w\s]", re.UNICODE)


def tokenize_preserve_spacing(text: str) -> List[str]:
    return _token_re.findall(text or "")


def normalize_for_compare(text: str) -> str:
    if not text:
        return ""
    collapsed = re.sub(r"\s+", " ", text)
    return collapsed.strip().lower()


