from fastapi import FastAPI
from pydantic import BaseModel

from chat.rag_chat_pipeline import chat


app = FastAPI()


class ChatRequest(BaseModel):
    question: str


@app.post("/chat")
def rag_chat(req: ChatRequest):

    result = chat(req.question)

    return result