# Indexer/config.py

import os

# Paths 
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRAWL_OUTPUT    = os.path.join(BASE_DIR, "sample_data", "news_ycombinator_com", "optimized")
JSONL_INPUT_DIR = os.path.join(CRAWL_OUTPUT, "jsonl")
RAW_HTML_DIR    = CRAWL_OUTPUT
INDEX_DIR       = os.path.join(BASE_DIR, "Indexer", "lucene_index")

## TODO: update CRAWL_OUTPUT to point to the full dataset when ready
# Field names for Lucene documents
TITLE_FIELD    = "title"
HEADERS_FIELD  = "headers"
BODY_FIELD     = "body"
URL_FIELD      = "url"
HTML_FILE_FIELD = "html_file"

# Field boost values for Lucene indexing
FIELD_BOOSTS = {
    TITLE_FIELD:   4.0,
    HEADERS_FIELD: 2.0,
    URL_FIELD:     2.0,
    BODY_FIELD:    1.0,
}

# Parameters for search and snippet generation
TOP_K          = 10
SNIPPET_LENGTH = 200