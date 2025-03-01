import requests
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from example.config import settings

# Replace with your OpenRouter API key
API_KEY = settings.DEEPSEEK_TOKEN.get_secret_value()
API_URL = 'https://openrouter.ai/api/v1/chat/completions'

# Define the headers for the API request
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Define the request payload (data)
data = {
    "model": "deepseek/deepseek-chat:free",
    "messages": [{"role": "user", "content": "What is the meaning of life?"}]
}

# Send the POST request to the DeepSeek API
response = requests.post(API_URL, json=data, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    print("API Response:", response.json()["choices"][0]["message"]["content"])
else:
    print("Failed to fetch data from API. Status Code:", response.status_code)