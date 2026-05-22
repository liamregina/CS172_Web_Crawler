# Indexer

## Setup
Make sure PyLucene is installed before running anything.
See the main README for installation instructions.

## Step 1: Run the crawler
```bash
python Crawler/crawler.py Crawler/seed.txt 20 2 yesOpt data
```

## Step 2: Build the index
```bash
./scripts/indexer.sh data/news_ycombinator_com/optimized Indexer/lucene_index
```

## Step 3: Test the searcher
```bash
python -m Indexer.searcher "your query here"
```

## Notes
- Always run commands from the project root (CS172_Web_Crawler/)
- Rebuild the index any time new crawl data comes in
- The index lives at Indexer/lucene_index/ and is gitignored
- Flask app only needs to call search(query_str) from Indexer/searcher.py
- If you get JVM thread errors in Flask, call lucene.getVMEnv().attachCurrentThread() at the top of your route handler