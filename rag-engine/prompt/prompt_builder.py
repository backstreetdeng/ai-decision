from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "templates" / "rag_prompt.txt"


def load_prompt_template():

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(question, contexts):

    context_text = ""

    for idx, ctx in enumerate(contexts):

        context_text += f"[Context {idx+1}]\n{ctx}\n\n"

    template = load_prompt_template()

    prompt = template.format(
        context=context_text,
        question=question
    )

    return prompt