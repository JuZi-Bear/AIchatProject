from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt_template(name: str) -> str:
    prompt_name = name if name.endswith(".md") else f"{name}.md"
    prompt_path = PROMPT_DIR / prompt_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt 模板不存在：{prompt_path}")

    return prompt_path.read_text(encoding="utf-8")


def render_prompt(template: str, variables: dict) -> str:
    rendered = template

    for key, value in (variables or {}).items():
        rendered = rendered.replace("{{" + str(key) + "}}", "" if value is None else str(value))

    return rendered


def render_prompt_by_name(name: str, variables: dict) -> str:
    return render_prompt(load_prompt_template(name), variables)
