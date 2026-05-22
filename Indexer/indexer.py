import sys
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List

import lucene

# Allowing the indexer to run correctly from the main project folder like 
# python Crawler/indexer/indexer.py data/<seed_folder>/optimized index
CURRENTDIR = Path(__file__).resolve().parent
PROJECTROOT = CURRENTDIR.parent.parent

if str(CURRENTDIR) not in sys.path:
    sys.path.insert(0, str(CURRENTDIR))

if str(PROJECTROOT) not in sys.path:
    sys.path.insert(0, str(PROJECTROOT))


# Start PyLucene JVM before importing Java/Lucene classes.
if lucene.getVMEnv() is None:
    lucene.initVM(vmargs=["-Djava.awt.headless=true"])
else:
    lucene.getVMEnv().attachCurrentThread()


from java.nio.file import Paths as JavaPaths
from org.apache.lucene.analysis.standard import StandardAnalyzer as LuceneStandardAnalyzer
from org.apache.lucene.document import Document as LuceneDocument
from org.apache.lucene.document import Field as LuceneField
from org.apache.lucene.document import TextField as LuceneTextField
from org.apache.lucene.document import StringField as LuceneStringField
from org.apache.lucene.document import StoredField as LuceneStoredField
from org.apache.lucene.index import IndexWriter as LuceneIndexWriter
from org.apache.lucene.index import IndexWriterConfig as LuceneIndexWriterConfig
from org.apache.lucene.index import DirectoryReader as LuceneDirectoryReader
from org.apache.lucene.store import FSDirectory as LuceneFSDirectory


try:
    from Indexer.document_loader import load_documents
except ImportError:
    from Crawler.indexer.document_loader import load_documents


def normalizeWhiteSpace(text: Any) -> str:
    if text is None:
        return ""

    return " ".join(str(text).split())


def computeContentHash(text: str) -> str:
    cleanedText = normalizeWhiteSpace(text).lower()
    return hashlib.sha256(cleanedText.encode("utf-8", errors="ignore")).hexdigest()


def getUsefulText(document: Dict[str, Any]) -> str:
    title = normalizeWhiteSpace(document.get("title"))
    headers = normalizeWhiteSpace(document.get("headers"))
    body = normalizeWhiteSpace(document.get("body"))

    return normalizeWhiteSpace(f"{title} {headers} {body}")


def hasUsefulText(document: Dict[str, Any]) -> bool:
    return len(getUsefulText(document)) > 0


def isGoodStatus(document: Dict[str, Any]) -> bool:
    status = document.get("status")

    if status is None or status == "":
        return True

    try:
        statusNumber = int(status)
    except ValueError:
        return True

    return 200 <= statusNumber < 400


def getContentHash(document: Dict[str, Any]) -> str:
    contentHash = normalizeWhiteSpace(document.get("content_hash"))

    if contentHash:
        return contentHash

    usefulText = getUsefulText(document)
    return computeContentHash(usefulText)


def outlinksToJsonString(outlinks: Any) -> str:
    if isinstance(outlinks, list):
        return json.dumps(outlinks, ensure_ascii=False)

    return "[]"


def makeLuceneDocument(document: Dict[str, Any]) -> Any:
    luceneDocument = LuceneDocument()

    docId = normalizeWhiteSpace(document.get("doc_id"))
    url = normalizeWhiteSpace(document.get("url"))
    title = normalizeWhiteSpace(document.get("title"))
    headers = normalizeWhiteSpace(document.get("headers"))
    body = normalizeWhiteSpace(document.get("body"))
    htmlFile = normalizeWhiteSpace(document.get("html_file"))
    depth = normalizeWhiteSpace(document.get("depth"))
    status = normalizeWhiteSpace(document.get("status"))
    contentHash = getContentHash(document)
    outlinks = outlinksToJsonString(document.get("outlinks"))

    # Searchable fields.
    luceneDocument.add(LuceneTextField("title", title, LuceneField.Store.YES))
    luceneDocument.add(LuceneTextField("headers", headers, LuceneField.Store.NO))
    luceneDocument.add(LuceneTextField("body", body, LuceneField.Store.NO))
    luceneDocument.add(LuceneTextField("url", url, LuceneField.Store.YES))

    # Stored fields for showing results later.
    luceneDocument.add(LuceneStringField("doc_id", docId, LuceneField.Store.YES))
    luceneDocument.add(LuceneStoredField("html_file", htmlFile))
    luceneDocument.add(LuceneStoredField("depth", depth))
    luceneDocument.add(LuceneStoredField("status", status))
    luceneDocument.add(LuceneStoredField("content_hash", contentHash))
    luceneDocument.add(LuceneStoredField("outlinks", outlinks))

    return luceneDocument


def openIndexDirectory(indexDir: str) -> Any:
    indexPath = Path(indexDir).resolve()
    indexPath.mkdir(parents=True, exist_ok=True)

    return LuceneFSDirectory.open(JavaPaths.get(str(indexPath)))


def verifyIndexCanOpen(indexDir: str) -> int:
    directory = openIndexDirectory(indexDir)
    reader = LuceneDirectoryReader.open(directory)

    numberOfDocuments = reader.numDocs()

    reader.close()
    directory.close()

    return numberOfDocuments


def getCleanDocuments(inputDir: str) -> List[Dict[str, Any]]:
    documents = load_documents(inputDir)

    if documents is None:
        return []

    return documents


def shouldSkipDocument(document: Dict[str, Any], seenUrls: set, seenContentHashes: set) -> str:
    url = normalizeWhiteSpace(document.get("url"))
    contentHash = getContentHash(document)

    if not hasUsefulText(document):
        return "empty"

    if not isGoodStatus(document):
        return "bad"

    if url and url in seenUrls:
        return "duplicate"

    if contentHash and contentHash in seenContentHashes:
        return "duplicate"

    return ""


def markDocumentSeen(document: Dict[str, Any], seenUrls: set, seenContentHashes: set) -> None:
    url = normalizeWhiteSpace(document.get("url"))
    contentHash = getContentHash(document)

    if url:
        seenUrls.add(url)

    if contentHash:
        seenContentHashes.add(contentHash)


def buildIndex(inputDir: str, indexDir: str) -> Dict[str, int]:
    print("Starting indexing...")

    inputPath = Path(inputDir)

    if not inputPath.exists():
        raise FileNotFoundError(f"Input folder does not exist: {inputDir}")

    documents = getCleanDocuments(inputDir)
    loadedCount = len(documents)

    print(f"Loaded documents: {loadedCount}")

    directory = openIndexDirectory(indexDir)
    analyzer = LuceneStandardAnalyzer()

    config = LuceneIndexWriterConfig(analyzer)
    config.setOpenMode(LuceneIndexWriterConfig.OpenMode.CREATE)

    writer = LuceneIndexWriter(directory, config)

    indexedCount = 0
    skippedEmptyCount = 0
    skippedDuplicateCount = 0
    skippedBadCount = 0

    seenUrls = set()
    seenContentHashes = set()

    try:
        for document in documents:
            try:
                skipReason = shouldSkipDocument(
                    document,
                    seenUrls,
                    seenContentHashes
                )

                if skipReason == "empty":
                    skippedEmptyCount += 1
                    continue

                if skipReason == "duplicate":
                    skippedDuplicateCount += 1
                    continue

                if skipReason == "bad":
                    skippedBadCount += 1
                    continue

                luceneDocument = makeLuceneDocument(document)
                writer.addDocument(luceneDocument)

                markDocumentSeen(document, seenUrls, seenContentHashes)
                indexedCount += 1

            except Exception as error:
                skippedBadCount += 1
                print(f"Skipping bad document because of error: {error}")

        writer.commit()

    finally:
        writer.close()
        directory.close()

    verifiedCount = verifyIndexCanOpen(indexDir)

    print(f"Indexed documents: {indexedCount}")
    print(f"Skipped empty documents: {skippedEmptyCount}")
    print(f"Skipped duplicate documents: {skippedDuplicateCount}")
    print(f"Skipped bad documents: {skippedBadCount}")
    print(f"Verified index documents: {verifiedCount}")
    print(f"Index saved to: {indexDir}")
    print("Done.")

    return {
        "loaded": loadedCount,
        "indexed": indexedCount,
        "skipped_empty": skippedEmptyCount,
        "skipped_duplicate": skippedDuplicateCount,
        "skipped_bad": skippedBadCount,
        "verified": verifiedCount,
    }


def main() -> None:
    if len(sys.argv) != 3:
        print("ERROR: Invalid arguments")
        print("Usage: python Crawler/indexer/indexer.py <input_dir> <index_dir>")
        print("Example: python Crawler/indexer/indexer.py data/<seed_folder>/optimized index")
        return

    inputDir = sys.argv[1]
    indexDir = sys.argv[2]

    buildIndex(inputDir, indexDir)


if __name__ == "__main__":
    main()