import json
from pathlib import Path


def build_graph(jsonl_dir):
    graph = {}

    for jsonl_file in Path(jsonl_dir).glob("*.jsonl"):
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)

                url = record.get("url")
                outlinks = record.get("outlinks", [])

                graph[url] = outlinks

    return graph


if __name__ == "__main__":
    graph = build_graph(
        "sample_data/news_ycombinator_com/optimized/jsonl"
    )

    print(f"Pages loaded: {len(graph)}")

    print(list(graph.keys())[:5])

    N = len(graph)

    ranks = {
        url: 1.0 / N
        for url in graph
    }

    print("Initial PageRank:")
    print(list(ranks.items())[:5])

    d = 0.85
    iterations = 20

    # Initialize PageRank
    ranks = {
        url: 1.0 / N
        for url in graph
    }

    for i in range(iterations):
        new_ranks = {}

    for page in graph:
        new_ranks[page] = (1 - d) / N

    for source in graph:

        outlinks = graph[source]

        valid_outlinks = [
            link
            for link in outlinks
            if link in graph
        ]

        if len(valid_outlinks) == 0:

            contribution = d * ranks[source] / N

            for page in graph:
                new_ranks[page] += contribution

            continue

        contribution = d * ranks[source] / len(valid_outlinks)

        for target in valid_outlinks:
            new_ranks[target] += contribution

    ranks = new_ranks

    print("\nAfter 20 iterations:")

    top_pages = sorted(
        ranks.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for url, score in top_pages[:10]:
        print(f"{score:.6f}  {url}")

    print("\nTotal rank:", sum(ranks.values()))

    ranks = new_ranks

    with open("pagerank_scores.json", "w") as f:
        json.dump(ranks, f, indent=2)

