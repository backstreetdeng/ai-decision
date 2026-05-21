# cli_rag_chat.py
from chat.rag_chat_pipeline import chat
import uuid

def main():
    print("=== 企业级 RAG Chat CLI 测试工具 ===")
    print("输入 'exit' 退出\n")

    # 每次启动 CLI 创建一个唯一 session_id
    session_id = str(uuid.uuid4())
    print(f"当前 session_id: {session_id}\n")

    while True:
        question = input("用户: ").strip()
        if question.lower() in ["exit", "quit"]:
            print("退出 CLI")
            break

        # 调用 RAG Chat
        result = chat(
            question=question,
            session_id=session_id,
            metadata_filter={"brand": "Tesla"},  # 可按需修改
            stream=True
        )

        print("\n\n=== FINAL ANSWER ===")
        print(result["answer"])

        print("\n=== CITATIONS ===")
        for c in result["citations"]:
            print(f"{c['file_name']} 第{c['page_number']}页 (score: {c['score']})")

        print("\n========================\n")

if __name__ == "__main__":
    main()