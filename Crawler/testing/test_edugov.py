import unittest
from Crawler.crawler import WebCrawler
from scrapy.crawler import CrawlerProcess
from filtering import is_valid_url

# Optionally, you can filter the domains that your crawler should access, e.g. .edu or .gov only.

class TestEduGov(unittest.TestCase):
    def setUp(self):
        self.crawler = WebCrawler()

    def test_gov_websites(self):

        gov_usa_url = "https://usa.gov"
        gov_ca_url = "https://usa.gov"
        pages = 2
        depth = 1

        test_crawl = CrawlerProcess(
            seeds=gov_usa_link,
            max_pages=pages,
            max_depth=depth,
            output_dir="testruns"
        )
        
        self.assertGreaterEqual(test_crawl["page_count"], 1)
    
    def test_edu_websites(self):
        edu_ucr_url = "https://ucr.edu"
        edu_ucla_url = "https://ucla.edu"
        pages = 2
        depth = 1

        test_crawl = CrawlerProcess(
            seeds=edu_ucr_url,
            max_pages=pages,
            max_depth=depth,
            output_dir="testruns"
        )
        
        self.assertGreaterEqual(test_crawl["page_count"], 1)
    
if __name__ == '__main__':
    unittest.main()
