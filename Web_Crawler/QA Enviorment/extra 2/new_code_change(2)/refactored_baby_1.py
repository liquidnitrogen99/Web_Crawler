from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging
import requests
import random
import time

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

        all_urls.add(current_url)
        category = categorize_url(current_url, start_domain)
        url_categories[category].add(current_url)
        logging.info(f"URL: {current_url} added to category: {category}")
    
    
    
    
    return


start_url = "https://www.lazybuddha.ai"
main(start_url)