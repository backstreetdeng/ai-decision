import requests


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