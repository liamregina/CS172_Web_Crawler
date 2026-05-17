from __future__ import annotations


def get_settings(outputDir: str,maxPages: int,maxDepth: int,threads: int = 32,targetTotalMb: int = 500,logLevel: str = "INFO",) -> dict:
    """
    Centralized Scrapy settings for the performance/efficiency role.

    Scrapy is asynchronous, so CONCURRENT_REQUESTS is the practical equivalent of the
    multi-threading requirement for this project. AutoThrottle keeps the crawler polite.
    """
    perDomain = max(1, min(8, threads // 4 if threads >= 4 else threads))

    return {
        "DEPTH_LIMIT": int(maxDepth),
        "CLOSESPIDER_ITEMCOUNT": int(maxPages),
        "LOG_LEVEL": logLevel,
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "CS172-WebCrawler/1.0 (+https://www.ucr.edu)",
        "CONCURRENT_REQUESTS": int(threads),
        "CONCURRENT_REQUESTS_PER_DOMAIN": perDomain,
        "DOWNLOAD_DELAY": 0.05,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 0.2,
        "AUTOTHROTTLE_MAX_DELAY": 5.0,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": float(perDomain),
        "COOKIES_ENABLED": False,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 2,
        "DOWNLOAD_TIMEOUT": 15,
        "DUPEFILTER_CLASS": "optimizer.dupefilters.CanonicalURLDupeFilter",
        "ITEM_PIPELINES": {
            "optimizer.pipelines.ContentDedupPipeline": 100,
            "optimizer.pipelines.LargeCrawlStoragePipeline": 300,
        },
        "OUTPUT_DIR": outputDir,
        "CRAWL_JSONL_ROTATE_MB": 10,
        "TARGET_TOTAL_MB": int(targetTotalMb),
        "STORE_RAW_HTML": True,
        "HTTPCACHE_ENABLED": False,
        "TELNETCONSOLE_ENABLED": False,
    }