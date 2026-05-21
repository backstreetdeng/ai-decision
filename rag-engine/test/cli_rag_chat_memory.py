import sys
import os
import uuid

# 确保上级目录在 sys.path，方便导入 chat 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chat.rag_chat_pipeline import chat

def main():
    print("=== 企业级 RAG Chat CLI 测试工具（支持 Chat Memory） ===")
    print("输入 'exit' 退出\n")

    # 生成唯一 session_id
    session_id = str(uuid.uuid4())
    print(f"当前 session_id: {session_id}\n")

    # 用户可输入品牌或车型做 metadata filter
    brand_filter = input("请输入品牌过滤（可空，默认 Tesla）：").strip() or "Tesla"
    car_model_filter = input("请输入车型过滤（可空）：").strip() or None
    metadata_filter = {"brand": brand_filter}
    if car_model_filter:
        metadata_filter["car_model"] = car_model_filter

    print("\n开始对话，输入你的问题...\n")

    while True:
        question = input("问题：").strip()
        if question.lower() in ["exit", "quit"]:
            print("退出 CLI")
            break

        # 调用 RAG Chat
        result = chat(
            question=question,
            session_id=session_id,
            metadata_filter=metadata_filter,
            stream=True  # Streaming 输出
        )

        print("\n\n=== ANSWER ===")
        print(result["answer"])

        print("\n=== CONTEXT ===")
        if result["contexts"]:
            for idx, ctx in enumerate(result["contexts"], start=1):
                # 打印前 200 字做预览
                print(f"--- Context {idx} ---")
                print(ctx[:200], "..." if len(ctx) > 200 else "")
        else:
            print("无上下文")

        print("\n=== CITATIONS ===")
        if result["citations"]:
            for c in result["citations"]:
                print(f"{c['file_name']} 第{c['page_number']}页 (score: {c['score']})")
        else:
            print("无引用")

        print("\n========================\n")


if __name__ == "__main__":
    main()