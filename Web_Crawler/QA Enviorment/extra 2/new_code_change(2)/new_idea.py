import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging
import time
import random
from queue import Queue

# Function to get links from a page
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


# Function to categorize a URL
def categorize_url(url, start_domain):
    parsed_url = urlparse(url)
    category = None

    domain = parsed_url.netloc.replace('www.', '')

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


# Function to crawl a website
def crawl_website(start_url):
    session = requests.Session()
    queue = Queue()
    queue.put(start_url)
    visited_urls = set()
    categorized_urls = {
        'Internal': set(),
        'External': set(),
        'Special': set(),
        'FTP': set(),
        'Media or Documents': set(),
        'Others': set()
    }

    while not queue.empty():
        current_url = queue.get()
        if current_url not in visited_urls:
            visited_urls.add(current_url)
            links, error = get_links_from_page(session, current_url)
            if not error:
                for link in links:
                    category = categorize_url(link, urlparse(start_url).netloc)
                    categorized_urls[category].add(link)
                    if link not in visited_urls and category == 'Internal':
                        queue.put(link)

    return categorized_urls

# Start the crawl (example usage)
start_url = "https://lazybuddha.ai"
all_categorized_urls = crawl_website(start_url) # all categorized url in this dict
internal_urls = all_categorized_urls['Internal'] # all urls from internal category
print("all category urls togather",all_categorized_urls)
print("only internal category urls",internal_urls)

