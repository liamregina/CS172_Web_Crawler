#!/usr/bin/env bash
set -e

SEED_FILE="$1"
NUM_PAGES="$2"
HOPS="$3"
OPTIMIZE="$4"
OUT_DIR="$5"
EXTRA_ARG="$6"

if [ -n "$EXTRA_ARG" ]; then
  echo "ERROR: Too many arguments."
  exit 1
fi

if [ -z "$SEED_FILE" ]; then
  echo "ERROR: Missing seed file."
  exit 1
fi

[ -z "$NUM_PAGES" ] && NUM_PAGES=10
[ -z "$HOPS" ] && HOPS=3

if [ -z "$OPTIMIZE" ]; then
  OPTIMIZE="noOpt"
  echo "OPTIMIZATION not provided. Using default: noOpt"
fi

if [ -z "$OUT_DIR" ]; then
  OUT_DIR="data"
  echo "OUTPUT_DIR not provided. Using default: data"
fi

cd "$(dirname "$0")/.."

python Crawler/crawler.py "$SEED_FILE" "$NUM_PAGES" "$HOPS" "$OPTIMIZE" "$OUT_DIR"