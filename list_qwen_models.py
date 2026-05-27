import os
import requests

api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()

if not api_key:
    raise RuntimeError("DASHSCOPE_API_KEY is not set")

url = "https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model": "qwen3.6-flash",
    "messages": [
        {"role": "user", "content": "用一句中文介绍你自己。"}
    ],
}

response = requests.post(url, headers=headers, json=payload)

print("Status:", response.status_code)
print(response.text)