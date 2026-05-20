from chat.rag_chat_pipeline import chat


query = "Model Y 电池保修多久"

result = chat(query)

print(result["answer"])

print(result["citations"])