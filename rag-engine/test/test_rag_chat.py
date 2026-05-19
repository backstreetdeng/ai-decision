from chat.rag_chat_pipeline import chat


query = "Model Y 电池保修多久"


result = chat(query)

print("\n========== QUESTION ==========\n")

print(result["question"])

print("\n========== ANSWER ==========\n")

print(result["answer"])

print("\n========== CONTEXT ==========\n")

for idx, ctx in enumerate(result["contexts"]):

    print(f"\n--- CONTEXT {idx+1} ---")

    print(ctx[:500])