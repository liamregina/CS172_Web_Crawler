'''This file loads crawler output from Part A and converts it into clean
document dictionaries for the indexer. '''

import json
import sys
from pathlib import Path

try:
    from Indexer.html_parser import clean_text, parse_html_file
except ImportError:
    from html_parser import clean_text, parse_html_file


def get_html_path(html_file, input_dir):

    # Try to find the real HTML file path.

    if not html_file:
        return ""

    path = Path(html_file)

    if path.exists():
        return str(path)

    input_path = Path(input_dir)

    possible_path = input_path / html_file
    if possible_path.exists():
        return str(possible_path)

    possible_path = input_path / Path(html_file).name
    if possible_path.exists():
        return str(possible_path)

    return str(html_file)


def make_document(item, doc_id, input_dir):

    #Convert one raw crawler item into one clean document.

    html_file = get_html_path(item.get("html_file", ""), input_dir)

    title = clean_text(item.get("title", ""))
    headers = clean_text(item.get("headers", ""))
    body = clean_text(item.get("body", ""))

    # If important text is missing, try reading the saved HTML file.
    if html_file and (not title or not body):
        parsed = parse_html_file(html_file)

        if not title:
            title = parsed["title"]

        if not headers:
            headers = parsed["headers"]

        if not body:
            body = parsed["body"]

    content_hash = item.get("content_hash", item.get("contentHash", ""))

    return {
        "doc_id": str(item.get("doc_id", doc_id)),
        "url": clean_text(item.get("url", "")),
        "title": title,
        "headers": headers,
        "body": body,
        "html_file": html_file,
        "outlinks": item.get("outlinks", []) if isinstance(item.get("outlinks", []), list) else [],
        "depth": item.get("depth", None),
        "status": item.get("status", None),
        "content_hash": clean_text(content_hash),
    }


def load_from_jsonl(input_dir):

    # Load documents from optimized JSONL crawler output.
 
    jsonl_dir = Path(input_dir) / "jsonl"

    if not jsonl_dir.exists():
        return []

    documents = []

    for jsonl_file in sorted(jsonl_dir.glob("*.jsonl")):
        with jsonl_file.open("r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue

                document = make_document(item, len(documents), input_dir)
                documents.append(document)

    return documents


def load_from_html(input_dir):
  
    # Fallback: if JSONL files do not exist, load raw HTML files directly.

    documents = []

    for html_file in sorted(Path(input_dir).glob("*.html")):
        parsed = parse_html_file(html_file)

        document = {
            "doc_id": str(len(documents)),
            "url": "",
            "title": parsed["title"],
            "headers": parsed["headers"],
            "body": parsed["body"],
            "html_file": str(html_file),
            "outlinks": [],
            "depth": None,
            "status": None,
            "content_hash": "",
        }

        documents.append(document)

    return documents


def load_documents(input_dir):

    # Main function Person 2 will probably use (Gokul)


    documents = load_from_jsonl(input_dir)

    if documents:
        return documents

    return load_from_html(input_dir)


def main():
    if len(sys.argv) != 2:
        print("Usage: python Indexer/document_loader.py data/<seed_folder>/optimized")
        return

    input_dir = sys.argv[1]
    documents = load_documents(input_dir)

    print(f"Loaded documents: {len(documents)}")

    if documents:
        first = documents[0]
        print(f"First URL: {first['url']}")
        print(f"First title: {first['title']}")
        print(f"First body length: {len(first['body'])}")


if __name__ == "__main__":
    main()