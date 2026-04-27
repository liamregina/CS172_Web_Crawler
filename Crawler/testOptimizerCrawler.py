"""
Place this file at:
    CS172_Web_Crawler/Crawler/testOptimizerCrawler.py

Run from the project root:
    python -u Crawler/testOptimizerCrawler.py

It tests:
- optimizer/url_utils.py
- optimizer/linkExtractor.py
- optimizer/dupefilters.py
- optimizer/pipelines.py
- performance.py
"""

from __future__ import annotations

import importlib
import json
import shutil
import sys
import tempfile
import threading
from contextlib import contextmanager
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from types import SimpleNamespace

CRAWLER_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CRAWLER_DIR.parent


def forceStdlibLogging() -> None:
    """Prevents Crawler/logging.py from shadowing Python's real logging module."""
    crawlerDirStr = str(CRAWLER_DIR)
    oldSysPath = list(sys.path)

    sys.path = [path for path in sys.path if Path(path or ".").resolve() != CRAWLER_DIR]

    existingLogging = sys.modules.get("logging")
    if existingLogging is not None:
        loggingFile = getattr(existingLogging, "__file__", "") or ""
        if loggingFile and Path(loggingFile).resolve() == (CRAWLER_DIR / "logging.py").resolve():
            del sys.modules["logging"]

    stdlibLogging = importlib.import_module("logging")
    if not hasattr(stdlibLogging, "getLogger"):
        raise RuntimeError("Could not import Python's standard logging module.")

    sys.modules["logging"] = stdlibLogging
    sys.path = oldSysPath

    if crawlerDirStr not in sys.path:
        sys.path.insert(0, crawlerDirStr)


forceStdlibLogging()


@contextmanager
def protectStdlibLoggingImports():
    forceStdlibLogging()
    yield
    forceStdlibLogging()


def printSection(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}")


def testUrlUtils() -> None:
    from optimizer.url_utils import (
        hasBlockedExtension,
        isAllowedDomain,
        isAllowedTld,
        normalizeUrl,
        shouldCrawlUrl,
    )

    printSection("1. Testing optimizer/url_utils.py")

    cleaned = normalizeUrl(
        "/A/B/../Page.html?utm_source=google&b=2&a=1#section",
        "https://Example.com:443/root/index.html",
    )
    require(
        cleaned == "https://example.com/A/Page.html?a=1&b=2",
        f"normalizeUrl removes fragments, tracking params, default ports, and normalizes path: {cleaned}",
    )

    require(normalizeUrl("mailto:test@example.com") is None, "mailto links are rejected")
    require(normalizeUrl("javascript:alert(1)") is None, "javascript links are rejected")
    require(hasBlockedExtension("https://example.com/file.pdf"), "PDF files are blocked")
    require(hasBlockedExtension("/image.PNG"), "image files are blocked case-insensitively")

    require(isAllowedDomain("https://cs.ucr.edu/page", "ucr.edu"), "subdomains are allowed")
    require(not isAllowedDomain("https://example.com/page", "ucr.edu"), "outside domains are rejected")
    require(isAllowedTld("https://www.ucr.edu/page", ".edu"), ".edu TLD is allowed")
    require(not isAllowedTld("https://example.com/page", ".edu"), "non-.edu TLD is rejected")

    require(
        shouldCrawlUrl("/about#team", "https://www.ucr.edu/index.html", allowedDomains="ucr.edu")
        == "https://www.ucr.edu/about",
        "shouldCrawlUrl returns the cleaned URL when it passes filters",
    )
    require(
        shouldCrawlUrl("https://example.com/file.pdf", allowedDomains="example.com") is None,
        "shouldCrawlUrl rejects blocked file types",
    )


class FakeSelectorList:
    def __init__(self, values: list[str]):
        self.values = values

    def getall(self) -> list[str]:
        return self.values


class FakeResponse:
    def __init__(self, url: str, hrefs: list[str]):
        self.url = url
        self.hrefs = hrefs

    def css(self, query: str):
        if query == "a::attr(href)":
            return FakeSelectorList(self.hrefs)
        return FakeSelectorList([])


def testLinkExtractor() -> None:
    from optimizer.linkExtractor import extractCleanLinks

    printSection("2. Testing optimizer/linkExtractor.py")

    response = FakeResponse(
        "https://www.ucr.edu/index.html",
        [
            "/about#top",
            "/about?utm_source=google",
            "/file.pdf",
            "mailto:test@example.com",
            "https://example.com/outside",
            "https://cs.ucr.edu/research",
            "https://cs.ucr.edu/research#fragment",
        ],
    )

    links = extractCleanLinks(response, allowedDomains="ucr.edu", maxLinksPerPage=10)
    print("Extracted links:", links)

    require("https://www.ucr.edu/about" in links, "relative links are cleaned and included")
    require("https://cs.ucr.edu/research" in links, "allowed subdomain links are included")
    require(all("pdf" not in link for link in links), "PDF links are removed")
    require(all("example.com" not in link for link in links), "outside-domain links are removed")
    require(len(links) == len(set(links)), "duplicate cleaned links are removed")


def testDupefilter() -> None:
    printSection("3. Testing optimizer/dupefilters.py")

    with protectStdlibLoggingImports():
        try:
            from scrapy import Request
        except Exception as exc:
            raise RuntimeError("Scrapy failed to import. Run: python -m pip install -r requirements.txt") from exc

    from optimizer.dupefilters import CanonicalURLDupeFilter

    dupeFilter = CanonicalURLDupeFilter()

    req1 = Request("https://example.com/page#top")
    req2 = Request("https://example.com/page?utm_source=google")
    req3 = Request("https://example.com/other")

    # Test both your camelCase method and Scrapy's required snake_case alias.
    require(dupeFilter.requestSeen(req1) is False, "first canonical URL is not a duplicate")
    require(dupeFilter.requestSeen(req2) is True, "same URL after normalization is detected as duplicate")
    require(dupeFilter.requestSeen(req3) is False, "different URL is not marked duplicate")

    require(hasattr(dupeFilter, "request_seen"), "Scrapy-compatible request_seen method exists")


def testPipelinesUnit() -> None:
    printSection("4. Testing optimizer/pipelines.py directly")

    with protectStdlibLoggingImports():
        from scrapy.exceptions import DropItem

    from optimizer.pipelines import (
        ContentDedupPipeline,
        LargeCrawlStoragePipeline,
        computeContentHash,
        computeUrlFilename,
    )

    require(
        computeContentHash("Hello    World") == computeContentHash("hello world"),
        "content hash ignores case and repeated whitespace",
    )
    require(computeUrlFilename("https://example.com/page").endswith(".html"), "URL filename ends with .html")

    dummySpider = SimpleNamespace(logger=SimpleNamespace(info=lambda *args, **kwargs: None))

    dedup = ContentDedupPipeline()
    item1 = {"url": "https://example.com/1", "body": "same page text"}
    item2 = {"url": "https://example.com/2", "body": "same   page   text"}
    item3 = {"url": "https://example.com/3", "body": "different page text"}

    require(dedup.processItem(item1, dummySpider)["contentHash"], "first content item is accepted")

    try:
        dedup.processItem(item2, dummySpider)
        raise AssertionError("duplicate content should have raised DropItem")
    except DropItem:
        print("PASS: duplicate content is dropped")

    require(dedup.processItem(item3, dummySpider)["contentHash"], "different content is accepted")
    require(hasattr(dedup, "process_item"), "Scrapy-compatible process_item method exists")

    outputDir = PROJECT_ROOT / "data" / "optimizer_pipeline_unit_test"
    if outputDir.exists():
        shutil.rmtree(outputDir)

    storage = LargeCrawlStoragePipeline(
        outputDir=str(outputDir),
        maxFileMb=1,
        targetTotalMb=50,
        storeRawHtml=True,
    )
    storage.openSpider(dummySpider)
    storage.processItem(
        {
            "url": "https://example.com/page",
            "title": "Test Page",
            "body": "Test body",
            "rawHtml": "<html><body>Test body</body></html>",
        },
        dummySpider,
    )
    storage.closeSpider(dummySpider)

    require(hasattr(storage, "from_crawler"), "Scrapy-compatible from_crawler classmethod exists")
    require(hasattr(storage, "open_spider"), "Scrapy-compatible open_spider method exists")
    require(hasattr(storage, "process_item"), "Scrapy-compatible process_item method exists")
    require(hasattr(storage, "close_spider"), "Scrapy-compatible close_spider method exists")

    htmlFiles = list((outputDir / "html").glob("*.html"))
    jsonlFiles = list((outputDir / "jsonl").glob("*.jsonl"))

    require(len(htmlFiles) == 1, "LargeCrawlStoragePipeline writes raw HTML file")
    require(len(jsonlFiles) == 1, "LargeCrawlStoragePipeline writes JSONL metadata file")

    with jsonlFiles[0].open("r", encoding="utf-8") as file:
        row = json.loads(file.readline())

    require("rawHtml" not in row, "rawHtml is removed from JSONL to avoid duplicate huge storage")
    require("html_file" in row, "JSONL row stores path to saved HTML file")


def testPerformanceSettings() -> None:
    printSection("5. Testing Crawler/performance.py")

    from performance import get_settings

    settings = get_settings(
        outputDir="data/optimizer_test_output",
        maxPages=10,
        maxDepth=2,
        threads=16,
        targetTotalMb=50,
        logLevel="WARNING",
    )

    require(settings["ROBOTSTXT_OBEY"] is True, "robots.txt obey setting is enabled")
    require(settings["CONCURRENT_REQUESTS"] == 16, "thread/concurrency setting is applied")
    require(settings["DEPTH_LIMIT"] == 2, "depth limit setting is applied")
    require(settings["CLOSESPIDER_ITEMCOUNT"] == 10, "max page count setting is applied")
    require(
        settings["DUPEFILTER_CLASS"] == "optimizer.dupefilters.CanonicalURLDupeFilter",
        "custom canonical duplicate filter is configured",
    )
    require("optimizer.pipelines.ContentDedupPipeline" in settings["ITEM_PIPELINES"], "content dedup pipeline is configured")
    require("optimizer.pipelines.LargeCrawlStoragePipeline" in settings["ITEM_PIPELINES"], "large crawl storage pipeline is configured")


def buildLocalSite(siteDir: Path) -> None:
    siteDir.mkdir(parents=True, exist_ok=True)

    (siteDir / "index.html").write_text(
        """
        <html>
            <head><title>Local Test Home</title></head>
            <body>
                <h1>Home Page</h1>
                <p>This is the home page for the optimizer integration test.</p>
                <a href="/page.html#section">Page with fragment</a>
                <a href="/page.html?utm_source=google">Same page with tracking query</a>
                <a href="/duplicate.html">Duplicate content page</a>
                <a href="/file.pdf">PDF should be skipped</a>
                <a href="mailto:test@example.com">Mail should be skipped</a>
            </body>
        </html>
        """,
        encoding="utf-8",
    )

    duplicateBody = """
        <html>
            <head><title>Duplicate Body Test</title></head>
            <body>
                <h1>Duplicate Body</h1>
                <p>This body text is intentionally the same so content hashing can drop one copy.</p>
            </body>
        </html>
    """
    (siteDir / "page.html").write_text(duplicateBody, encoding="utf-8")
    (siteDir / "duplicate.html").write_text(duplicateBody, encoding="utf-8")
    (siteDir / "file.pdf").write_text("fake pdf", encoding="utf-8")


class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def runLocalHttpServer(siteDir: Path):
    handler = lambda *args, **kwargs: QuietHTTPRequestHandler(*args, directory=str(siteDir), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def testMiniScrapyIntegration() -> None:
    printSection("6. Testing mini Scrapy crawl integration")

    with protectStdlibLoggingImports():
        try:
            import scrapy
            from scrapy.crawler import CrawlerProcess
        except Exception as exc:
            raise RuntimeError("Scrapy failed to import. Run: python -m pip install -r requirements.txt") from exc

    from optimizer.linkExtractor import extractCleanLinks
    from performance import get_settings

    outputDir = PROJECT_ROOT / "data" / "optimizer_test_output"
    if outputDir.exists():
        shutil.rmtree(outputDir)

    with tempfile.TemporaryDirectory() as tmp:
        siteDir = Path(tmp) / "site"
        buildLocalSite(siteDir)
        server = runLocalHttpServer(siteDir)
        port = server.server_address[1]
        startUrl = f"http://127.0.0.1:{port}/index.html"
        allowedDomain = f"127.0.0.1:{port}"

        class OptimizerTestSpider(scrapy.Spider):
            name = "optimizer_test_spider"

            def __init__(self, startUrl: str, allowedDomain: str, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.start_urls = [startUrl]
                self.allowedDomainsCustom = [allowedDomain]

            def parse(self, response):
                title = response.css("title::text").get(default="").strip()
                headers = " ".join(response.css("h1::text, h2::text, h3::text").getall())
                body = " ".join(response.css("body *::text").getall())

                cleanLinks = extractCleanLinks(
                    response=response,
                    allowedDomains=self.allowedDomainsCustom,
                    maxLinksPerPage=50,
                )

                yield {
                    "url": response.url,
                    "title": title,
                    "headers": headers,
                    "body": body,
                    "outlinks": cleanLinks,
                    "rawHtml": response.text,
                    "status": response.status,
                }

                for link in cleanLinks:
                    yield scrapy.Request(link, callback=self.parse, dont_filter=False)

        settings = get_settings(
            outputDir=str(outputDir),
            maxPages=10,
            maxDepth=2,
            threads=8,
            targetTotalMb=50,
            logLevel="ERROR",
        )

        process = CrawlerProcess(settings=settings)
        process.crawl(OptimizerTestSpider, startUrl=startUrl, allowedDomain=allowedDomain)
        process.start()
        server.shutdown()

    htmlDir = outputDir / "html"
    jsonlDir = outputDir / "jsonl"
    require(htmlDir.exists(), "mini crawl created html output directory")
    require(jsonlDir.exists(), "mini crawl created jsonl output directory")

    htmlFiles = list(htmlDir.glob("*.html"))
    jsonlFiles = list(jsonlDir.glob("*.jsonl"))

    require(len(htmlFiles) >= 2, f"mini crawl stored at least 2 unique HTML pages, found {len(htmlFiles)}")
    require(len(jsonlFiles) >= 1, f"mini crawl stored at least 1 JSONL file, found {len(jsonlFiles)}")

    rows = []
    for jsonlFile in jsonlFiles:
        with jsonlFile.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    rows.append(json.loads(line))

    print(f"Mini crawl stored {len(rows)} JSONL rows")
    for row in rows:
        print(" -", row.get("title"), row.get("url"))

    require(all("contentHash" in row for row in rows), "all stored rows include contentHash")
    require(all("html_file" in row for row in rows), "all stored rows include html_file path")
    require(all("rawHtml" not in row for row in rows), "rawHtml is not duplicated inside JSONL")
    require(all(not row["url"].endswith(".pdf") for row in rows), "PDF URL was not crawled/stored")

    duplicateBodyPages = [row for row in rows if "Duplicate Body Test" in row.get("title", "")]
    require(len(duplicateBodyPages) == 1, "content duplicate pipeline dropped one of the two identical-body pages")


def main() -> None:
    printSection("CS172 optimizer test runner")
    print("Project root:", PROJECT_ROOT)
    print("Crawler dir:", CRAWLER_DIR)

    testUrlUtils()
    testLinkExtractor()
    testDupefilter()
    testPipelinesUnit()
    testPerformanceSettings()
    testMiniScrapyIntegration()

    printSection("ALL OPTIMIZER TESTS PASSED")
    print("Your camelCase optimizer files are working by themselves and with a mini Scrapy crawl.")
    print("Generated test output folder:", PROJECT_ROOT / "data" / "optimizer_test_output")


if __name__ == "__main__":
    main()
