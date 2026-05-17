import os
import sys
import time
from urllib.parse import urlsplit

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider

import filtering
import storage
from logging_utils import log_page


class WebCrawler(scrapy.Spider):
    name = "web_crawler"

    def __init__(self,seeds,max_pages,max_depth,optimize,output_dir,allowed_domains_custom=None,allowed_tlds_custom=None,
        *args,**kwargs):

        super().__init__(*args, **kwargs)
        self.start_urls = seeds
        self.max_pages = int(max_pages)
        self.max_depth = int(max_depth)
        self.optimize = bool(optimize)
        self.output_dir = output_dir
        self.allowed_domains_custom = allowed_domains_custom or []
        self.allowed_tlds_custom = allowed_tlds_custom or []

        self.page_count = 0
        self.visited = set()

        os.makedirs(output_dir, exist_ok=True)

    def parse(self, response):
        if self.page_count >= self.max_pages:
            raise CloseSpider(f"Reached max page limit of {self.max_pages}")

        # The basic crawler handles duplicate responses with this set
        # The optimized crawler also has Scrapy's CanonicalURLDupeFilter enabled
        if response.url in self.visited:
            return
        self.visited.add(response.url)

        current_depth = response.meta.get("depth", 0)
        page_index = self.page_count
        self.page_count += 1

        if self.optimize:
            clean_links = self.get_optimized_links(response)

            title = response.css("title::text").get(default="").strip()
            headers = " ".join(response.css("h1::text, h2::text, h3::text").getall()).strip()
            body = " ".join(response.css("body *::text").getall()).strip()

            self.logger.info("[OPTIMIZED] Crawled %s: %s", page_index, response.url)

            # In optimized mode, storage is handled by optimizer.pipelines.LargeCrawlStoragePipeline
            yield {
                "url": response.url,
                "title": title,
                "headers": headers,
                "body": body,
                "outlinks": clean_links,
                "rawHtml": response.text,
                "status": response.status,
                "depth": current_depth,
            }
        else:
            # In noOpt mode we do NOT call optimizer code and just save each HTML page directly
            storage.save_page(response, self.output_dir, page_index)
            log_page(page_index, response.url)
            clean_links = filtering.get_valid_links(response,allowed_domains=self.allowed_domains_custom)

        if self.page_count >= self.max_pages:
            raise CloseSpider(f"Reached max page limit of {self.max_pages}")

        if current_depth < self.max_depth:
            for link in clean_links:
                if link not in self.visited:
                    yield scrapy.Request(link, callback=self.parse, dont_filter=False)

    def get_optimized_links(self, response):
        from optimizer.linkExtractor import extractCleanLinks

        return extractCleanLinks(response=response,allowedDomains=self.allowed_domains_custom,allowedTlds=self.allowed_tlds_custom,
            maxLinksPerPage=200)


def read_seed_file(seed_file):
    with open(seed_file, "r", encoding="utf-8") as file:
        seeds = [line.strip() for line in file if line.strip()]

    if not seeds:
        raise ValueError(f"Seed file is empty: {seed_file}")

    return seeds


def domain_from_seed(seed_url):
    # Handles normal seeds like https://www.ucr.edu and also plain seeds like www.ucr.edu.
    candidate = seed_url if "://" in seed_url else "https://" + seed_url
    parsed = urlsplit(candidate)
    host = (parsed.hostname or "").lower()

    if host.startswith("www."):
        host = host[4:]

    # For .edu and .gov seeds, allow the whole organization domain, so cs.ucr.edu is allowed for ucr.edu.
    labels = host.split(".")
    if len(labels) >= 2 and labels[-1] in {"edu", "gov"}:
        host = ".".join(labels[-2:])

    return host


def build_allowed_domains(seeds):
    allowed = []
    for seed in seeds:
        domain = domain_from_seed(seed)
        if domain and domain not in allowed:
            allowed.append(domain)
    return allowed


def build_settings(optimize, output_dir, max_pages, max_depth):
    if optimize:
        # Lazy import so noOpt mode does not call optimizer/performance settings.
        from performance import get_settings

        settings = get_settings(outputDir=output_dir,maxPages=int(max_pages),maxDepth=int(max_depth),threads=32,targetTotalMb=500,
            logLevel="INFO")
        settings["CLOSESPIDER_PAGECOUNT"] = int(max_pages)
        return settings

    return {
        "DEPTH_LIMIT": int(max_depth),
        "CLOSESPIDER_PAGECOUNT": int(max_pages),
        "LOG_LEVEL": "INFO",
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "CS172-BasicCrawler/1.0 (+https://www.ucr.edu)",
        "CONCURRENT_REQUESTS": 8,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "DOWNLOAD_DELAY": 0.10,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "COOKIES_ENABLED": False,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 1,
        "DOWNLOAD_TIMEOUT": 15,
        "TELNETCONSOLE_ENABLED": False,
    }


def main():
    if len(sys.argv) != 6:
        print("ERROR: Invalid arguments")
        print("If using Windows OS Use: scripts\\crawler.bat <seed_file> <num_pages> <depth> <yesOpt/noOpt> <output_dir>")
        print("If using Mac OS Use: scripts/crawler.sh <seed_file> <num_pages> <depth> <yesOpt/noOpt> <output_dir>")
        return

    seed_file = sys.argv[1]
    num_pages = int(sys.argv[2])
    depth = int(sys.argv[3])
    opt_flag = sys.argv[4].strip().lower()
    output_dir = sys.argv[5]

    if opt_flag not in {"yesopt", "noopt"}:
        print("ERROR: Optimization flag must be yesOpt or noOpt")
        return

    optimize = opt_flag == "yesopt"
    seeds = read_seed_file(seed_file)
    allowed_domains = build_allowed_domains(seeds)

    os.makedirs(output_dir, exist_ok=True)

    # Keep the two runs separate so yesOpt and noOpt do not overwrite each other.
    crawl_dir = storage.seed_folder_store(seeds[0], output_dir)
    run_mode = "optimized" if optimize else "basic"
    run_output_dir = os.path.join(crawl_dir, run_mode)
    os.makedirs(run_output_dir, exist_ok=True)

    if optimize:
        print("Running optimized crawler: yesOpt")
        print("Optimizer enabled: canonical URL filtering, content dedup, JSONL rotation, raw HTML storage, and higher concurrency.")
    else:
        print("Running basic crawler: noOpt")
        print("Optimizer disabled: using normal filtering.py + storage.py only.")

    print(f"Seeds loaded: {len(seeds)}")
    print(f"Allowed domains: {allowed_domains}")
    print(f"Output folder: {run_output_dir}")

    settings = build_settings(optimize=optimize,output_dir=run_output_dir,max_pages=num_pages,max_depth=depth)

    process = CrawlerProcess(settings=settings)
    process.crawl(WebCrawler,seeds=seeds,max_pages=num_pages,max_depth=depth,optimize=optimize,output_dir=run_output_dir,
        allowed_domains_custom=allowed_domains)

    start_time = time.perf_counter()
    process.start()
    elapsed_time = time.perf_counter() - start_time

    print("\n========== CRAWL SUMMARY ==========")
    print(f"Mode: {run_mode} ({opt_flag})")
    print(f"Seed file: {seed_file}")
    print(f"Max pages requested: {num_pages}")
    print(f"Max depth requested: {depth}")
    print(f"Output folder: {run_output_dir}")
    print(f"Query/crawl runtime: {elapsed_time:.2f} seconds")
    print("===================================")


if __name__ == "__main__":
    main()
