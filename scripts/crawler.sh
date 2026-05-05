#!/usr/bin/env bash
set -e

# Usage:
# ./scripts/crawler.sh Crawler/seed.txt 10000 6 data/crawl_output

SEED_FILE="$1"
NUM_PAGES="$2"
HOPS="$3"
OUT_DIR="$4"
EXTRA_ARG="$5"

# Too many arguments
if [ -n "$EXTRA_ARG" ]; then
  echo "ERROR: Too many arguments."
  echo "Usage: ./scripts/crawler.sh Crawler/seed.txt [num_pages] [depth] [output_dir]"
  exit 1
fi

# Missing required seed file
if [ -z "$SEED_FILE" ]; then
  echo "ERROR: Missing seed file."
  echo "Usage: ./scripts/crawler.sh Crawler/seed.txt [num_pages] [depth] [output_dir]"
  exit 1
fi

# Defaults
if [ -z "$NUM_PAGES" ]; then
  NUM_PAGES=10000
  echo "NUM_PAGES not provided. Using default: 10000"
fi

if [ -z "$HOPS" ]; then
  HOPS=6
  echo "DEPTH not provided. Using default: 6"
fi

if [ -z "$OUT_DIR" ]; then
  OUT_DIR="data"
  echo "OUTPUT_DIR not provided. Using default: data"
fi

cd "$(dirname "$0")/.."

python Crawler/crawler.py "$SEED_FILE" "$NUM_PAGES" "$HOPS" "$OUT_DIR"