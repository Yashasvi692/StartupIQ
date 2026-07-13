from pathlib import Path

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def read_text(path: str | Path, encoding: str = "utf-8") -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return file_path.read_text(encoding)


def write_text(path: str | Path, content: str, encoding: str = "utf-8") -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding)
    logger.info("Written %d bytes to %s", len(content), file_path)


async def read_text_async(path: str | Path, encoding: str = "utf-8") -> str:
    from asyncio import to_thread

    return await to_thread(read_text, path, encoding)


async def write_text_async(path: str | Path, content: str, encoding: str = "utf-8") -> None:
    from asyncio import to_thread

    await to_thread(write_text, path, content, encoding)
