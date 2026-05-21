# Indexer/snippet.py

import re
import string

# TODO: this is the wrapper. call by searcher.py
def get_snippet(body: str, query: str) -> str:
    """
    Find the first occurrence of any query term in the body text and return
    ~150-250 characters of surrounding context as a snippet.
    If no query term is found, return the first 200 characters of the body.
    """
    if not body:
        return ""

    terms = _tokenize_query(query)

    # No usable terms in query. Return the opening of the body
    if not terms:
        return body[:200] + ("..." if len(body) > 200 else "")

    body_lower = body.lower()
    match_index = _find_match_index(body_lower, terms)

    # NOTE: user it not informed if no match was found. 
    # No query term found anywhere in the body. Fall back to opening
    if match_index == -1:
        return body[:200] + ("..." if len(body) > 200 else "")

    return _extract_window(body, match_index)

# helpers 
def _find_match_index(body_lower: str, terms: list[str]) -> int:
    """
    Search for the first occurrence of any query term in the lowercased body.
    Returns the character index of the first match, or -1 if none found.
    Uses word boundaries so 'the' does not match inside 'there'.
    """
    earliest = -1

    for term in terms:
        match = re.search(r'\b' + re.escape(term) + r'\b', body_lower)
        if match:
            idx = match.start()
            # track the earliest match across all terms
            if earliest == -1 or idx < earliest:
                earliest = idx

    return earliest

def _extract_window(body: str, match_index: int, window: int = 200) -> str:
    """
    Extract a window of text centered around match_index.
    Clamps to the start/end of the body and adds ellipses where text is cut off.
    "Snaps" to word boundaries so the snippet does not cut mid-word.
    """
    half = window // 2
    start = max(0, match_index - half)
    end = min(len(body), match_index + half)

    # Snap start forward to the nearest word boundary
    if start > 0:
        space = body.rfind(" ", 0, start)
        if space != -1:
            start = space + 1

    # Snap end forward to the nearest word boundary
    if end < len(body):
        space = body.find(" ", end)
        if space != -1:
            end = space

    snippet = body[start:end].strip()

    # Add ellipses to signal that text was cut off on either side
    if start > 0:
        snippet = "..." + snippet
    if end < len(body):
        snippet = snippet + "..."

    return snippet

def _tokenize_query(query: str) -> list[str]:
    """
    Split the query string into individual lowercased terms,
    strip punctuation (ex. 'python,' and 'python' are treated the same)
    """
    query = query.lower()
    query = query.translate(str.maketrans("", "", string.punctuation))
    return [term for term in query.split() if term]