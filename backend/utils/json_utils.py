import json
from pathlib import Path
from typing import Any

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def to_json(data: Any, indent: int = 2) -> str:
    return json.dumps(data, indent=indent, default=str, ensure_ascii=False)


def from_json(text: str) -> Any:
    return json.loads(text)


def read_json(path: str | Path) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with file_path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, data: Any, indent: int = 2) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
    logger.info("Written JSON to %s", file_path)


def safe_serialize(data: Any) -> Any:
    try:
        json.dumps(data)
        return data
    except (TypeError, ValueError):
        return str(data)
