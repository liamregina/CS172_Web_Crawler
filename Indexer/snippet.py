# Indexer/snippet.py

# wrapper
def get_snippet(body: str, query: str) -> str:
    """
    Find the first occurrence of any query term in the body text and return
    ~150-250 characters of surrounding context as a snippet.
    If no query term is found, return the first 200 characters of the body.
    """
    pass

# helper
def _find_match_index(body_lower: str, terms: list[str]) -> int:
    """
    Search for the first occurrence of any query term in the lowercased body.
    Returns the character index of the first match, or -1 if none found.
    """
    pass


def _extract_window(body: str, match_index: int, window: int = 200) -> str:
    """
    Extract a window of text centered around match_index.
    Clamps to the start/end of the body and adds ellipses where text is cut off.
    """
    pass


def _tokenize_query(query: str) -> list[str]:
    """
    Split the query string into individual lowercased terms,
    stripping punctuation so 'python,' and 'python' are treated the same.
    """
    pass