from llm.clients.qwen_client import generate


def generate_answer(prompt: str):

    answer = generate(prompt)

    return answer