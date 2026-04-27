from __future__ import annotations
import hashlib
import json
from pathlib import Path
from scrapy.exceptions import CloseSpider, DropItem


def normalizeTextForHash(text: str | None) -> str:
    """Normalize body/html text so duplicate hashes are stable."""
    if not text:
        return ""
    return " ".join(str(text).lower().split())


def computeContentHash(text: str | None) -> str:
    normalized = normalizeTextForHash(text)
    return hashlib.sha256(normalized.encode("utf-8", errors="ignore")).hexdigest()


def computeUrlFilename(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8", errors="ignore")).hexdigest() + ".html"


class ContentDedupPipeline:
    # Drop duplicate page content after the crawler downloads a page

    def __init__(self):
        self.seenContentHashes: set[str] = set()
        self.duplicatesDropped = 0

    def processItem(self, item, spider):
        text = item.get("body") or item.get("plain_text") or item.get("text") or item.get("rawHtml") or ""
        contentHash = computeContentHash(text)

        if not normalizeTextForHash(text):
            self.duplicatesDropped += 1
            raise DropItem(f"Empty content dropped: {item.get('url')}")

        if contentHash in self.seenContentHashes:
            self.duplicatesDropped += 1
            raise DropItem(f"Duplicate content dropped: {item.get('url')}")

        self.seenContentHashes.add(contentHash)
        item["contentHash"] = contentHash
        return item

    def closeSpider(self, spider):
        spider.logger.info("Duplicate/empty pages dropped: %s", self.duplicatesDropped)

    # Keeping this consistent with camel casing
    def process_item(self, item, spider):
        return self.processItem(item, spider)

    def close_spider(self, spider):
        return self.closeSpider(spider)


class LargeCrawlStoragePipeline:
    """
    Store the crawl in a project-friendly format.

    Output:
    - outputDir/html/*.html for all crawled HTML files
    - outputDir/jsonl/crawl_00000.jsonl, rotating around 10 MB each
    """

    def __init__(self, outputDir: str, maxFileMb: int, targetTotalMb: int, storeRawHtml: bool):
        self.outputDir = Path(outputDir)
        self.maxFileBytes = maxFileMb * 1024 * 1024
        self.targetTotalBytes = targetTotalMb * 1024 * 1024
        self.storeRawHtml = storeRawHtml

        self.dataDir = self.outputDir / "jsonl"
        self.htmlDir = self.outputDir / "html"

        self.fileIndex = 0
        self.currentFile = None
        self.currentFileBytes = 0
        self.totalBytes = 0
        self.itemCount = 0

    @classmethod
    def fromCrawler(cls, crawler):
        return cls(
            outputDir=crawler.settings.get("OUTPUT_DIR", "data/crawl_output"),
            maxFileMb=crawler.settings.getint("CRAWL_JSONL_ROTATE_MB", 10),
            targetTotalMb=crawler.settings.getint("TARGET_TOTAL_MB", 500),
            storeRawHtml=crawler.settings.getbool("STORE_RAW_HTML", True),
        )

    def openSpider(self, spider):
        self.dataDir.mkdir(parents=True, exist_ok=True)
        if self.storeRawHtml:
            self.htmlDir.mkdir(parents=True, exist_ok=True)
        self.openNextFile()

    def closeSpider(self, spider):
        if self.currentFile:
            self.currentFile.close()
        spider.logger.info("Stored unique pages: %s", self.itemCount)
        spider.logger.info("Stored approximately %.2f MB", self.totalBytes / (1024 * 1024))

    def processItem(self, item, spider):
        item = dict(item)
        rawHtml = item.get("rawHtml", "")

        if self.storeRawHtml and rawHtml:
            htmlFilename = computeUrlFilename(item.get("url", ""))
            htmlPath = self.htmlDir / htmlFilename
            htmlPath.write_text(rawHtml, encoding="utf-8", errors="ignore")
            item["html_file"] = str(htmlPath)
            item["raw_html_bytes"] = len(rawHtml.encode("utf-8", errors="ignore"))
            item.pop("rawHtml", None)

        line = json.dumps(item, ensure_ascii=False) + "\n"
        encoded = line.encode("utf-8", errors="ignore")

        if self.currentFileBytes + len(encoded) > self.maxFileBytes:
            self.openNextFile()

        self.currentFile.write(line)
        self.currentFileBytes += len(encoded)
        self.totalBytes += len(encoded) + int(item.get("raw_html_bytes", 0))
        self.itemCount += 1

        if self.totalBytes >= self.targetTotalBytes:
            raise CloseSpider(f"Reached target crawl size of {self.targetTotalBytes / (1024 * 1024):.1f} MB")

        return item

    def openNextFile(self):
        if self.currentFile:
            self.currentFile.close()
        outputPath = self.dataDir / f"crawl_{self.fileIndex:05d}.jsonl"
        self.currentFile = outputPath.open("w", encoding="utf-8")
        self.currentFileBytes = 0
        self.fileIndex += 1

    # Keeping this consistent with camel casing
    def process_item(self, item, spider):
        return self.processItem(item, spider)

    def close_spider(self, spider):
        return self.closeSpider(spider)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.fromCrawler(crawler)

    def open_spider(self, spider):
        return self.openSpider(spider)

    def close_spider(self, spider):
        return self.closeSpider(spider)

    def process_item(self, item, spider):
        return self.processItem(item, spider)
