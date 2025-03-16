import sys
import requests

path = sys.argv[-1]

with open(path) as file:
    data = file.read()


response = requests.post(
    'http://127.0.0.1:4321/find-url',
    json={
        'html-page': data
    }
)

print(f'Got response', response)
print(response.text)
