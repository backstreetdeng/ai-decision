# rag-engine/test/test_metadata_filter.py
import sys
import os

# 确保上级目录在 sys.path，方便导入 chat 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chat.rag_chat_pipeline import chat

if __name__ == "__main__":
    result = chat(
        question="Model Y 电池保修多久",
        # metadata_filter={"brand": "Tesla", "car_model": "Model Y"}
        metadata_filter={"brand": ["Tesla", "BYD"], "car_model": "Model"} # 多值匹配和模糊匹配
    )

    print("\n========== ANSWER ==========\n")
    print(result["answer"])

    print("\n========== CITATIONS ==========\n")
    for c in result["citations"]:
        print(f"{c['file_name']} 第{c['page_number']}页 (score: {c['score']})")