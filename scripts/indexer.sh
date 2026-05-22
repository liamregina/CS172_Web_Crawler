#!/usr/bin/env bash

# Usage:
# scripts/indexer.sh data/<seed_folder>/optimized index

INPUT_DIR="$1"
INDEX_DIR="$2"
EXTRA_ARG="$3"

if [ -n "$EXTRA_ARG" ]; then
    echo "ERROR: Too many arguments."
    echo "Usage: scripts/indexer.sh data/<seed_folder>/optimized [index_dir]"
    exit 1
fi

if [ -z "$INPUT_DIR" ]; then
    echo "ERROR: Missing input directory."
    exit 1
fi

if [ -z "$INDEX_DIR" ]; then
    INDEX_DIR="index"
    echo "INDEX_DIR not provided. Using default: index"
fi

cd "$(dirname "$0")/.."

python Crawler/indexer/indexer.py "$INPUT_DIR" "$INDEX_DIR"