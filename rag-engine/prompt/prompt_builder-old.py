from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "templates" / "rag_prompt.txt"


def build_prompt(question: str, contexts: list[str]) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    context_text = "\n\n".join(contexts)

    return template.format(
        context=context_text,
        question=question
    )