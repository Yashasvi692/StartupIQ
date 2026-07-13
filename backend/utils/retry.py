import asyncio
import functools
from collections.abc import Callable
from typing import TypeVar

from backend.utils.logger import get_logger

T = TypeVar("T")

logger = get_logger(__name__)


async def retry_async(
    func: Callable[..., T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    last_exception = None
    current_delay = delay

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(
                    "Attempt %d/%d failed: %s. Retrying in %.1fs...",
                    attempt + 1,
                    max_retries,
                    str(e),
                    current_delay,
                )
                await asyncio.sleep(current_delay)
                current_delay *= backoff

    raise last_exception


def retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_async(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                delay=delay,
                backoff=backoff,
                exceptions=exceptions,
            )

        return wrapper

    return decorator
