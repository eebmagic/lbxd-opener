import sys
import requests

path = sys.argv[-1]

with open(path) as file:
    data = file.read()


ROOT = 'http://127.0.0.1:4124'
response = requests.post(
    f'{ROOT}/find-url',
    json={
        'html-page': data
    }
)

print(f'Got response', response)
print(response.text)
