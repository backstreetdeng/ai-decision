from llm.clients.qwen_client import generate, generate_stream


def generate_answer(prompt: str):

    return generate(prompt)

def generate_answer_stream(prompt: str):
    """
    流式生成回答（返回生成器，需迭代调用）
    """    
    # 返回生成器
    return generate_stream(prompt)