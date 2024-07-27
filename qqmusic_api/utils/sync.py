"""代码来源: [bilibili-api](https://github.com/Nemo2011/bilibili-api)

同步执行异步函数
"""

import asyncio
from collections.abc import Coroutine
from typing import Any, TypeVar

T = TypeVar("T")


def __ensure_event_loop() -> None:
    try:
        asyncio.get_event_loop()

    except Exception:
        asyncio.set_event_loop(asyncio.new_event_loop())


def sync(coroutine: Coroutine[Any, Any, T]) -> T:
    """同步执行异步函数

    Args:
        coroutine (Coroutine): 异步函数

    Returns:
        该异步函数的返回值
    """
    __ensure_event_loop()
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)
