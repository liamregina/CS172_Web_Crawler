#!/usr/bin/env bash
set -e

# Usage:
# ./scripts/crawler.sh Crawler/seed.txt 10000 6 data/crawl_output

SEED_FILE=${1:-}
NUM_PAGES=${2:-10000}
HOPS=${3:-6}
OUT_DIR=${4:-data/crawl_output}

if [ -z "$SEED_FILE" ]; then
  echo "Missing seed file."
  echo "Usage: ./scripts/crawler.sh Crawler/seed.txt 10000 6 data/crawl_output"
  exit 1
fi

cd "$(dirname "$0")/.."
python Crawler/crawler.py "$SEED_FILE" "$NUM_PAGES" "$HOPS" "$OUT_DIR"
