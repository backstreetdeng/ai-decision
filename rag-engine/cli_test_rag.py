# cli_test_rag.py
import json
from chat.rag_chat_pipeline import chat

def parse_metadata_filter(input_str: str):
    """
    将用户输入的 JSON 字符串转换成 dict
    """
    try:
        return json.loads(input_str)
    except Exception:
        print("Metadata filter 格式错误，使用空字典")
        return {}

def main():
    print("=== 企业级 RAG Chat CLI 测试工具 ===")
    print("可输入问题并选择 metadata 过滤条件 Model Y 电池保修多久")
    print("输入 'exit' 退出\n")

    while True:
        question = input("请输入问题: ").strip()
        if question.lower() == "exit":
            break

        metadata_input = input(
            "请输入 metadata filter (JSON格式, 可选, 回车跳过): "
        ).strip()
        metadata_filter = parse_metadata_filter(metadata_input) if metadata_input else None

        print("\n正在生成答案... (streaming 输出)\n")

        result = chat(
            question=question,
            metadata_filter=metadata_filter,
            stream=True  # 实时输出
        )

        print("\n\n========== FINAL ANSWER ==========")
        print(result["answer"])

        print("\n========== CITATIONS ==========")
        for c in result["citations"]:
            print(f"{c['file_name']} 第{c['page_number']}页 (score: {c['score']})")

        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()