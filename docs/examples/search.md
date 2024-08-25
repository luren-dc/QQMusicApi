# 搜索

## 综合搜索

```python
import asyncio

from qqmusic_api import search

print(
    asyncio.run(
        search.general_search(
            "周杰伦",
            page=1,
            highlight=False,
        )
    )
)
```

## 类型搜索

```python
import asyncio

from qqmusic_api import search

print(
    asyncio.run(
        search.search_by_type(
            "周杰伦",
            search_type=search.SearchType.SINGER,
            page=1,
            highlight=False,
        )
    )
)
```

## 快速搜索

```python
import asyncio

from qqmusic_api import search

print(
    asyncio.run(
        search.quick_search(
            "周杰伦",
        )
    )
)
```
