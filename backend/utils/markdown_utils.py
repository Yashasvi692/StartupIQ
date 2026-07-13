from typing import Any


def h1(text: str) -> str:
    return f"# {text}\n"


def h2(text: str) -> str:
    return f"## {text}\n"


def h3(text: str) -> str:
    return f"### {text}\n"


def bold(text: str) -> str:
    return f"**{text}**"


def italic(text: str) -> str:
    return f"*{text}*"


def code(text: str) -> str:
    return f"`{text}`"


def link(text: str, url: str) -> str:
    return f"[{text}]({url})"


def list_item(text: str) -> str:
    return f"- {text}"


def table(headers: list[str], rows: list[list[str]]) -> str:
    result = []
    result.append("| " + " | ".join(headers) + " |")
    result.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        result.append("| " + " | ".join(row) + " |")
    return "\n".join(result) + "\n"


def code_block(text: str, language: str = "") -> str:
    return f"```{language}\n{text}\n```\n"


def quote(text: str) -> str:
    return f"> {text}\n"


def horizontal_rule() -> str:
    return "---\n"


def sanitize(text: str) -> str:
    replacements = {
        "_": r"\_",
        "*": r"\*",
        "`": r"\`",
        "[": r"\[",
        "]": r"\]",
    }
    for char, escaped in replacements.items():
        text = text.replace(char, escaped)
    return text


def render_section(heading: str, body: Any) -> str:
    return h2(heading) + "\n" + str(body) + "\n\n"
