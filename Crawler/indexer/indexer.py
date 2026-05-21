import json
import sys
import hashlib
from pathlib import Path
from typing import Dict, Iterator, Any

import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField, StringField, StoredField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.store import FSDirectory

def normalizeWhiteSpace(text: Any) -> str:
    if text is None:
        return ""
    return " ".join(str(text).split())

def computeContentHash(text: str) -> str:
    cleaned = normalizeWhiteSpace(text).lower()
    return hashlib.sha256(cleaned.encode("utf-8", errors="ignore")).hexdigest()

def loadDocuments(inputDir: str) -> Iterator[Dict[str, Any]]:
    """
    Temporary document loader for your current project.

    Expected current optimized crawler format:
        data/<seed_folder>/optimized/jsonl/crawl_00000.jsonl
    """

    inputPath = Path(inputDir)
    jsonlDir = inputPath/ "jsonl"

    if jsonlDir.exists():
        jsonlFiles = sorted(jsonlDir.glob("*.jsonl"))
    else:
        jsonlFiles = sorted(inputDir.glob("*.jsonl"))
    
    if not jsonlFiles:
        raise FileNotFoundError(
            f"No JSONL files found in {jsonlDir} or {inputPath}. "
            f"Make sure you are indexing the optimized crawler folder."
        )

    for json1File in jsonlFiles:
        with json1File.open("r", encoding="utf-8", errors="ignore") as file:
            for lineNumber, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    doc = json.loads(line)
                except json.JSONDecodeError:
                    print(f"Skipping bad JSON line: {json1File}:{lineNumber}")
                    continue
                
                yield doc

def initalizeLucence() -> None:
    """
    Starts PyLucene's Java VM if it is not already started.
    If it is already started, attach this thread to the VM.
    """