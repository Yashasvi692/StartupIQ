from pathlib import Path

from backend.utils.exceptions import PromptNotFoundError
from backend.utils.logger import get_logger

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
_cache: dict[str, str] = {}

logger = get_logger(__name__)


def get_prompt(name: str) -> str:
    if name in _cache:
        return _cache[name]

    prompt_path = PROMPTS_DIR / f"{name}.md"

    if not prompt_path.exists():
        raise PromptNotFoundError(f"Prompt '{name}' not found at {prompt_path}")

    content = prompt_path.read_text(encoding="utf-8")
    _cache[name] = content
    logger.info("Loaded prompt '%s' (%d chars)", name, len(content))
    return content


async def get_prompt_async(name: str) -> str:
    if name in _cache:
        return _cache[name]

    prompt_path = PROMPTS_DIR / f"{name}.md"

    if not await _async_exists(prompt_path):
        raise PromptNotFoundError(f"Prompt '{name}' not found at {prompt_path}")

    content = await _async_read_text(prompt_path)
    _cache[name] = content
    logger.info("Loaded prompt '%s' (%d chars)", name, len(content))
    return content


def clear_cache() -> None:
    _cache.clear()
    logger.info("Prompt cache cleared")


async def _async_exists(path: Path) -> bool:
    from asyncio import to_thread

    return await to_thread(path.exists)


async def _async_read_text(path: Path) -> str:
    from asyncio import to_thread

    return await to_thread(path.read_text, encoding="utf-8")
