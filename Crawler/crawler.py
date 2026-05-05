import scrapy
from scrapy.crawler import CrawlerProcess
import sys
import os

#temporary function stubs for testing



def save_page(response, output_dir, page_count):
    filename = os.path.join(output_dir, f"page_{page_count}.html")
    with open(filename, "wb") as f:
        f.write(response.body)

def log_page(count, url):
    print(f"Crawled {count}: {url}")

# IMPORTS FROM YOUR MODULES
#from crawler.filtering import get_valid_links
from filtering import get_valid_links
# from crawler.storage import save_page
from storage import save_page
# from crawler.logging_utils import log_page
from logging_utils import log_page
# from crawler.performance import get_settings
from performance import get_settings



class WebCrawler(scrapy.Spider):
    name = "web_crawler"

    def __init__(self, seeds, max_pages, max_depth, output_dir):
        self.start_urls = seeds
        self.max_pages = int(max_pages)
        self.max_depth = int(max_depth)
        self.output_dir = output_dir

        self.page_count = 0
        self.visited = set()

        os.makedirs(output_dir, exist_ok=True)

    def parse(self, response):
        # Stop if max pages reached
        if self.page_count >= self.max_pages:
            return

        # Avoid duplicates
        if response.url in self.visited:
            return
        self.visited.add(response.url)

        save_page(response, self.output_dir, self.page_count)
        log_page(self.page_count, response.url)

        self.page_count += 1

        # Follow links if within depth
        current_depth = response.meta.get("depth", 0)

        if current_depth < self.max_depth:
            links = get_valid_links(response)

            for link in links:
                if link.startswith("http"):
                    yield response.follow(link, self.parse)


# -------- CLI ENTRY POINT --------

def main():
    if len(sys.argv) != 5:
        print("Usage: python crawler.py <seed_file> <num_pages> <depth> <output_dir>")
        return

    seed_file = sys.argv[1]
    num_pages = sys.argv[2]
    depth = sys.argv[3]
    output_dir = sys.argv[4]

    with open(seed_file) as f:
        seeds = [line.strip() for line in f if line.strip()]

    process = CrawlerProcess({
        "DEPTH_LIMIT": int(depth),
        "LOG_LEVEL": "ERROR",
    })

    process.crawl(WebCrawler,
                  seeds=seeds,
                  max_pages=num_pages,
                  max_depth=depth,
                  output_dir=output_dir)

    process.start()

if __name__ == "__main__":
    main()