import requests
import json

prompt = "Создай задачу: завтра в 9 утра встреча с Петей"
response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "mistral",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    },
    timeout=60
)

print("RAW response:")
print(response.text)
