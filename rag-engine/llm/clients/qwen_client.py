import requests
import json  # 新增：用于安全解析JSON

OLLAMA_URL = "http://192.168.3.146:11434/api/generate"


def generate(prompt: str):

    payload = {
        "model": "qwen2.5:14b-instruct",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=300
    )

    response.raise_for_status()

    return response.json()["response"]

def generate_stream(prompt: str):
    """
    Streaming 生成器
    每次 yield 一小段生成内容
    """
    payload = {
        "model": "qwen2.5:14b-instruct",
        "prompt": prompt,
        "stream": True
    }

    with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300) as response:
        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            line = line.strip()
            try:
                data = json.loads(line)
                token = data.get("response")
                if token:
                    yield token
                if data.get("done", False):
                    break
            except json.JSONDecodeError:
                continue                        