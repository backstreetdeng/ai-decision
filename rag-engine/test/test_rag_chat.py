from chat.rag_chat_pipeline import chat


query = "Model Y 电池保修多久"


result = chat(query)

print("\n========== QUESTION ==========\n")

print(result["question"])

print("\n========== ANSWER ==========\n")

print(result["answer"])

print("\n========== CITATIONS ==========\n")
for c in result["citations"]:
    print(f"{c['file_name']} 第{c['page_number']}页 (score: {c['score']})")