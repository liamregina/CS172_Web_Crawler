import json
import os

def test_pagerank_file_exists():
    assert os.path.exists("pagerank_scores.json")

def test_pagerank_sums_to_one():
    with open("pagerank_scores.json") as f:
        ranks = json.load(f)

    total = sum(ranks.values())

    assert abs(total - 1.0) < 0.0001

def test_pagerank_not_empty():
    with open("pagerank_scores.json") as f:
        ranks = json.load(f)

    assert len(ranks) > 0