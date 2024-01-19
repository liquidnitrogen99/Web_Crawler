from bs4 import BeautifulSoup
import requests
import json
import time

def fetch_html(url):
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    print(f"Fetching HTML took {duration:.2f} ms.")
    return response.text

def read_html_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    organized_content = {}
    heading_stack = []

    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'span']):
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            heading_text = element.get_text(separator=' ', strip=True)

            heading_stack = heading_stack[:level-1] + [heading_text]
            current_heading = " - ".join(heading_stack)

            if current_heading not in organized_content:
                organized_content[current_heading] = []
        elif element.name in ['p', 'ul', 'span']:
            text = element.get_text(separator=' ', strip=True)
            if heading_stack:
                current_heading = " - ".join(heading_stack)
                organized_content[current_heading].append(text)

    return organized_content

def create_content_dict(organized_content, url):
    full_text = ""
    for heading, contents in organized_content.items():
        full_text += "start\n" + heading + "\n\n" + "\n".join(contents) + "\nend\n\n"

    return {
        "webpage_url": url,
        "text_chunk": full_text.strip()
    }

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def read_urls_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().splitlines()

# Main execution
url_file_path = 'C:/Trusted folder/Web_Crawler/QA Enviorment/visited_urls.txt'  # Replace with your file path
urls = read_urls_from_file(url_file_path)

all_data = []

for url in urls:
    html_content = fetch_html(url)
    organized_content = parse_html(html_content)
    content_dict = create_content_dict(organized_content, url)
    all_data.append(content_dict)

save_to_json(all_data, 'output.json')

#all_data is the final dict