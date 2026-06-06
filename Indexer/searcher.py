# Indexer/searcher.py
# Accepts a query string from the Flask app, searches the PyLucene index,
# and returns the top 10 results ranked by Lucene score.
# Each result includes rank, title, url, score, snippet, and html_file.
# Depends on snippet.py for snippet generation and config.py for shared constants.
from email import parser
import json
_searcher_cache = None
_pagerank_cache = None

import lucene
import sys
# Java standard library
from java.nio.file import Paths
from java.util import HashMap
from java.lang import Float

# PyLucene
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.queryparser.classic import MultiFieldQueryParser

# Local
from Indexer.config import HEADERS_FIELD, INDEX_DIR, TOP_K, FIELD_BOOSTS, TITLE_FIELD, URL_FIELD, BODY_FIELD, HTML_FILE_FIELD
from Indexer.snippet import get_snippet

_searcher_cache = None

def init_jvm() -> None:
    """
    Initialize the PyLucene JVM. Must be called once before any Lucene
    operations. Safe to call multiple times

    NOTE: Do not call this from the Flask app directly. search() calls it
    internally. Calling it twice from different places will cause a crash.
    """

    if not lucene.getVMEnv():
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])


def get_searcher():
    """
    Open and cache the IndexSearcher against the index at INDEX_DIR.
    Returns the cached instance on subsequent calls so the index
    is not reopened on every query (that would be expensive).

    NOTE (Flask): Every Flask worker thread must call
    lucene.getVMEnv().attachCurrentThread() before this function runs.
    If you are getting JVM thread errors this is why.

    NOTE (Person 2): The index must exist at the path defined in config.INDEX_DIR
    before this is called. Run indexer.py first to build it.
    """
    global _searcher_cache

    init_jvm()
    lucene.getVMEnv().attachCurrentThread()

    if _searcher_cache is not None:
        return _searcher_cache
    
    directory = FSDirectory.open(Paths.get(INDEX_DIR))
    reader = DirectoryReader.open(directory)
    _searcher_cache = IndexSearcher(reader)

    return _searcher_cache

def search(query_str: str, k: int = TOP_K) -> list[dict]:
    """
    Main entry point. Accepts a query string, searches the Lucene index
    across all fields with boosting, and returns the top k results.
    Each result is a dict with: rank, title, url, score, snippet, html_file.

    NOTE (Flask): This is the only function you need to call. Pass the
    string from the search box directly. Example:
        results = search(request.form['query'])
    Returns an empty list if nothing is found, never raises an exception.

    NOTE (Person 2): If results are coming back with empty title/url/body,
    it means those fields were not stored in the index. Make sure you are
    using Field.Store.YES for all fields in indexer.py.
    """
    if not query_str or not query_str.strip():
        return []

    try:
        index_searcher = get_searcher()  # returns cached searcher
        analyzer = StandardAnalyzer()
        query = _build_query(query_str, analyzer)
        top_docs = index_searcher.search(query, k)

        results = []
        for rank, score_doc in enumerate(top_docs.scoreDocs, start=1):
            result = _hit_to_dict(
                index_searcher,
                score_doc,
                rank,
                query_str
            )
            results.append(result)

        # Re-rank using combined Lucene + PageRank score
        results.sort(
            key=lambda r: r["score"],
            reverse=True
        )

        # Fix ranks after reordering
        for i, result in enumerate(results, start=1):
            result["rank"] = i

        return results

    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise


def _build_query(query_str: str, analyzer):
    """
    Build a MultiFieldQueryParser (def below)
    across title, headers, url, and body
    with boosts defined in config.FIELD_BOOSTS.
    Returns a Lucene Query object.

    NOTE MultipleFieldQueryParser: is a Lucene class that allows searching across multiple fields
    with different boosts. You pass it the list of fields to search, the analyzer (which tokenizes 
    the query the same way the indexer tokenized the documents), and the boosts HashMap telling it 
    how much each field matters. 
   
     NOTE (Person 2): The field names used here are pulled from config.py.
    If your indexed field names do not match config.py exactly, every
    query will return zero results. 
    """
    fields = [TITLE_FIELD, HEADERS_FIELD, BODY_FIELD, URL_FIELD]
    
    # Lucene expects boosts as a Java HashMap with Java Float values
    # FIXME: apply boosts after front-end integration
    boosts = HashMap()
    for field, boost in FIELD_BOOSTS.items():
        boosts.put(field, Float(boost))

    parser = QueryParser("body", analyzer)
    query = parser.parse(query_str)
    return query

def _hit_to_dict(index_searcher, score_doc, rank: int, query_str: str) -> dict:
    """
    Convert a single Lucene ScoreDoc hit into a result dict.
    Retrieves stored fields from the document and calls get_snippet
    to generate the snippet from the body text.
    Returns: { rank, title, url, score, snippet, html_file }

    NOTE (Person 2): This function calls doc.get() on title, url, body,
    and html_file. If any of these return None it means that field was
    not stored when you built the index. Use Field.Store.YES for all of them.
    """

    # Charlette Note: I changed this to work on my end, uncomment for y'alls

    # doc = index_searcher.doc(score_doc.doc)
    
    doc = index_searcher.storedFields().document(score_doc.doc)

    title       = doc.get(TITLE_FIELD)      or ""
    url         = doc.get(URL_FIELD)        or ""
    body_text   = doc.get(BODY_FIELD)       or ""
    html_file   = doc.get(HTML_FILE_FIELD)  or ""

    pagerank_scores = get_pagerank_scores()

    pagerank_score = float(
        pagerank_scores.get(url, 0.0)
    )

    combined_score = (
        0.85 * score_doc.score
        + 0.15 * pagerank_score
    )

    return {
        "rank": rank, # the loop in search() assigns rank by hits
        "title": title,
        "url": url,
        "score": combined_score,
        "pagerank": pagerank_score,
        "snippet": get_snippet(body_text, query_str, title),
        "html_file": html_file,
    }
    
# TODO: run 'python -m Indexer.searcher "your query here"' to test after index is built
# FIXME: REMOVE THIS WHEN DONE. SEE NOTE BELOW
def main():
    """

    print("Loaded PageRank entries:", len(get_pagerank_scores()))
    python3 -m Indexer.searcher "ucr"

    CLI entry point for testing. Takes a query from sys.argv and prints
    the top results to the terminal.
    Usage: python -m Indexer.searcher "your query here"

    NOTE: This is for testing only. The Flask app calls search() directly,
    not main(). You need to build the index with indexer.py before this works.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m Indexer.searcher \"your query here\"")
        return

    query_str = " ".join(sys.argv[1:])
    print(f"Searching for: {query_str}\n")

    results = search(query_str)

    if not results:
        print("No results found.")
        return

    for result in results:
        print(f"[{result['rank']}] {result['title']}")
        print(f"    URL:   {result['url']}")
        print(f"    Score: {result['score']:.4f}")
        print(f"    {result['snippet']}")
        print()

def get_pagerank_scores():
    global _pagerank_cache

    if _pagerank_cache is not None:
        return _pagerank_cache

    try:
        with open("pagerank_scores.json", "r") as f:
            _pagerank_cache = json.load(f)
    except FileNotFoundError:
        _pagerank_cache = {}

    return _pagerank_cache

if __name__ == "__main__":
    main()
    




