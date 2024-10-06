"""同步执行异步函数

代码来源: https://github.com/Nemo2011/bilibili-api
"""

import asyncio
from collections.abc import Coroutine
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

T = TypeVar("T")


def sync(coroutine: Coroutine[Any, Any, T]) -> T:
    """同步执行异步函数

    Args:
        coroutine: 执行异步函数所创建的协程对象

    Returns:
        该协程对象的返回值
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)
    else:
        with ThreadPoolExecutor() as executor:
            return executor.submit(asyncio.run, coroutine).result()
