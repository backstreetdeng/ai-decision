from typing import TypedDict


class RetrievedDocument(TypedDict):
    document: str
    score: float
    metadata: dict