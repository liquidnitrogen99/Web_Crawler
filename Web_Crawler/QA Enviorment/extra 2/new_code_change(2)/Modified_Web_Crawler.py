import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging
import random
import time

def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        handlers=[
                            logging.FileHandler("scraping_log.txt"),
                            logging.StreamHandler()
                        ])

def get_links_from_page(session, url, retry_count=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": urlparse(url).scheme + "://" + urlparse(url).netloc
    }
    
    for _ in range(retry_count):
        try:
            response = session.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            links = [urljoin(url, link.get('href')) for link in soup.find_all('a', href=True)]
            return set(links), False
        except requests.RequestException as e:
            logging.error(f"Failed to fetch {url}, retrying... ({e})")
            time.sleep(random.uniform(0.1, 0.5))
    
    logging.error(f"Giving up on {url} after {retry_count} failed attempts.")
    return set(), True

def categorize_url(url, start_domain):
    parsed_url = urlparse(url)
    category = None

    domain = parsed_url.netloc.replace('www.', '')

    # Define various categories based on URL characteristics
    if parsed_url.scheme.lower() in ['http', 'https']:
        if domain == start_domain.replace('www.', ''):
            category = 'Internal'
        else:
            category = 'External'
    elif parsed_url.scheme.lower() in ['mailto', 'tel']:
        category = 'Special'
    elif parsed_url.scheme.lower() == 'ftp':
        category = 'FTP'

    exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
    if any(url.lower().endswith(ext) for ext in exts):
        category = 'Media or Documents'

    if not category:
        category = 'Others'
    return category


def process_internal_url(url):
    
    # Define your processing logic here
    
    print(f"Processing internal URL: {url}")

def main(start_url):
    setup_logging()
    start_domain = urlparse(start_url).netloc
    to_visit, all_urls = {start_url}, set()
    url_categories = {'Internal': set(), 'External': set(), 'Special': set(), 'FTP': set(), 'Media or Documents': set(), 'Others': set()}

    session = requests.Session()

    url_count = 0
    start_time_internal = None
    while to_visit:
        current_url = to_visit.pop()
        
        logging.info(f"Visiting: {current_url}")

        all_urls.add(current_url)  # Add to all_urls set
        category = categorize_url(current_url, start_domain)
        url_categories[category].add(current_url)  # Update category set
        logging.info(f"URL: {current_url} added to category: {category}")

        if category == 'Internal':
            if start_time_internal is None:  # Start the timer when first "Internal" URL is encountered
                start_time_internal = time.time()
            process_internal_url(current_url)  # Process internal URLs in real-time

        # Integrity Check
        for cat, urls in url_categories.items():
            if cat != category and current_url in urls:
                logging.warning(f"URL: {current_url} is in multiple categories")

        new_links, is_failed = get_links_from_page(session, current_url)
        if not is_failed:
            filtered_links = set(filter(lambda url: categorize_url(url, start_domain) != 'Others', new_links))
            to_visit.update(filtered_links - all_urls)  # Avoid re-visiting URLs

        url_count += 1
        if url_count % 10 == 0:  # Every 10 URLs, print the size of each set
            for cat, urls in url_categories.items():
                logging.info(f"Category '{cat}' has {len(urls)} URLs")
            logging.info(f"Total URLs collected: {len(all_urls)}")

        if url_count > 100:
            break
        time.sleep(random.uniform(0.005, 0.05))

    if start_time_internal is not None:
        end_time_internal = time.time()
        duration_internal = end_time_internal - start_time_internal
        print(f"Time taken to collect 'Internal' URLs: {duration_internal:.2f} seconds")

    # Post-Execution Verification
    for category, urls in url_categories.items():
        print(f"Category: {category}, URLs: {urls}")
        print(f"Category: {category}, Num of URLs: {len(urls)}")
    print(f"All URLs: {len(all_urls)}")
    logging.info("Scraping complete.")

if __name__ == "__main__":
    start_url = "https://www.lazybuddha.ai"
    main(start_url)

