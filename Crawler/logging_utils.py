import scrapy
import pandas as pd
import os

def log_page(count, url):
    print(f"Crawled {count}: {url}")

# testing different seeds
def seed_testing(base_path):

    results = []
    for i in range(1, 6):
        csv_path = os.path.join(base_path, f'test{i}.csv')
        seeds = pd.read_csv(csv_path)
        
        category = seeds.columns[0]
        urls = seeds.iloc[:, 0].tolist()[1:] 
        
        results[category] = urls
        print(f"Category '{category}': {len(urls)} seeds")
        
        # test each seed in this category
        for url in urls:
            proper_crawl_test(url)
    
    return results


# verifying output folder fills
def output_folder_testing(output_dir):

    results = {
        "total_files": 0,
        "trailing_whitespace": 0,
        "errors": []
    }
    
    # checking if the output directory exists
    if not os.path.exists(output_dir):
        results["errors"].append(f"Output directory does not exist: {output_dir}")
        return results
    
    # count HTML files
    html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
    results["total_files"] = len(html_files)

    return results 



# checking for crashes
def proper_crawl_test(seed):

    print(f"Testing crawl session: {seed}")
    
    # returns a report for a crawl session
    report = pd.DataFrame({
        "Metric": ["Total Duration", "Average URL crawl duration", "Depth Crawled", "URLS stored"],
        "Value": ["N/A", "N/A", "N/A", "N/A"]
    })

    # run the crawl with function
    # STUB FOR CRAWLING SESSION + seed input

    # Not sure how the crawling is gonna work so temporarily nothing here, but it will log each of these

    return report


def main():
    proper_crawl_test([''])

if __name__ == "__main__":
    main()