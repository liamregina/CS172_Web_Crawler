# Indexer/snippet.py
# Sentence-based snippet generation.
# Splits the body into sentences, scores each by query term overlap,
# and returns the highest scoring sentence as the snippet.
# Falls back to the first sentence if no query terms are found.

import re
import string


def get_snippet(body: str, query: str, title: str = "") -> str:
    """
    Main entry point. Splits body into sentences, scores each by how many
    query terms it contains, and returns the best scoring sentence.
    Falls back to the first sentence if no terms match.
    """
    if not body:
        return ""

    
    terms = _tokenize_query(query)
    sentences = _split_sentences(body)
   
    # filter out sentences that start with the title
    if title:
        sentences = [s for s in sentences 
                        if not s.lower().startswith(title.lower()[:30])]
    
    if not sentences:
        # no clean sentences found. strip dots and return first 200 chars
        cleaned = re.sub(r'\.+', ' ', body).strip()
        cutoff = cleaned.find('.', 200)
        if cutoff != -1:
            return cleaned[:cutoff + 1]
        return cleaned[:200]

    if not terms:
        return sentences[0]

    best = _find_best_sentence(sentences, terms)
    return best


def _split_sentences(body: str) -> list[str]:
    """
    Split body text into sentences on '.', '!', '?'.
    Filters out very short sentences (under 20 chars) that are likely
    nav links or boilerplate.
    """
    raw = re.split(r'(?<=[.!?])\s+', body)
    return [
        s.strip() for s in raw 
        if len(s.strip()) >= 60
        and '|' not in s  # filter out sentences with '|' which are likely nav links
    ]


def _score_sentence(sentence: str, terms: list[str]) -> int:
    """
    Count how many query terms appear in the sentence.
    Higher score means more query terms matched.
    """
    sentence_lower = sentence.lower()
    return sum(
        1 for term in terms
        if re.search(r'\b' + re.escape(term) + r'\b', sentence_lower)
    )


def _find_best_sentence(sentences: list[str], terms: list[str]) -> str:
    """
    Score each sentence and return the highest scoring one.
    Falls back to the first sentence if nothing scores above 0.
    """
    best_sentence = sentences[0]
    best_score = 0

    for sentence in sentences:
        score = _score_sentence(sentence, terms)
        if score > best_score:
            best_score = score
            best_sentence = sentence
    
    # ensure ends with punctuation
    if not best_sentence.endswith(('.', '!', '?')):
        best_sentence = best_sentence.rstrip() + '.'

    return best_sentence

def _tokenize_query(query: str) -> list[str]:
    """
    Split the query string into individual lowercased terms,
    stripping punctuation so 'python,' and 'python' are treated the same.
    """
    query = query.lower()
    query = query.translate(str.maketrans("", "", string.punctuation))
    return [term for term in query.split() if term]