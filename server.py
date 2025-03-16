from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

import requests
import re
import sys

app = Flask(__name__)

TAG_TITLE = "PZPZlf ssJ7i B5dxMb"
TAG_META = "iAIpCb PZPZlf"


def get_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    div = soup.find('div', class_=TAG_TITLE)
    
    title = None
    if div:
        title = div.get_text(strip=True)

    return title

def get_meta(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
        div = soup.find('div', class_=TAG_META)
        spans = div.find_all('span')
    except AttributeError:
        return None
    
    year, genre, runtime = None, None, None
    if div:
        data = spans[-1].get_text(strip=True)
        parts = data.split(' ‧ ')

        if len(parts) == 3:
            year, genre, runtime = parts

    return {
        'title': get_title(html),
        'year': year,
        'genre': genre,
        'runtime': runtime,
    }


def infer_urls(meta):
    title = meta['title']
    year = meta['year']


    cleaned = title.lower()
    cleaned = re.sub(r'[^a-z0-9\-\ ]', '', cleaned)
    cleaned = cleaned.replace(' ', '-')

    # Sorted in "niche" order
    urls = [
        f'https://letterboxd.com/film/{cleaned}-{year}/',
        f'https://letterboxd.com/film/{cleaned}/',
    ]

    return urls


def check_urls(urls):
    pattern = r'\"https:\/\/boxd\.it\/[a-zA-Z0-9]+\"'
    for url in urls:
        response = requests.get(url)
        if response.ok:
            matches = re.findall(pattern, response.text)
            print(f'found all boxd links: ', matches)

            if len(matches) > 0:
                return matches[0][1:-1]
            return url

    return None


@app.route('/find-url', methods=['POST'])
def find_url():
    print(f'Processing request ...')
    html = request.json.get('html-page')
    print(f'Got html payload of char len: {len(html):,}')
    if not html or len(html) == 0:
        return "No html-page arg found in payload", 400

    meta = get_meta(html)
    if not meta:
        return "Could not infer metadata from payload", 500

    candidate_urls = infer_urls(meta)
    url = check_urls(candidate_urls)
    if not url:
        return f"None of the urls appeared valid. Tried these: {urls}", 500

    print(f'Returning: {url}\n')

    return url


if __name__ == '__main__':
    app.run(debug=True, port=4124)
