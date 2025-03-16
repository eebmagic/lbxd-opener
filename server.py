from bs4 import BeautifulSoup
import sys
import requests
import re
from flask import Flask, request, jsonify, status
from flask_cors import CORS

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
    
    div = soup.find('div', class_=TAG_META)
    spans = div.find_all('span')
    
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
    for url in urls:
        response = requests.get(url)
        if response.ok:
            return url

    return None


@app.route('/find-url', methods=['POST'])
def find_url():
    print(f'Processing request ...')
    html = request.json.get('html-page')
    print(f'Got html payload of char len: {len(html):,}')
    if not html or len(html) == 0:
        return "No html-page arg found in payload", status.HTTP_400_BAD_REQUEST

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
