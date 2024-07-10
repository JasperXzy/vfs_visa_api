import time

import requests
import json

# Target URL
url = 'http://127.0.0.1:5000/api/v1/'

# Load JSON File
with open('test_post.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Send POST Request
response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})

print(response.text)
