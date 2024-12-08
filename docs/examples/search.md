# 搜索

```python
from qqmusic_api import search, sync
```

## 示例：综合搜索

```python
sync(
    search.general_search(
        "周杰伦",
        page=1,
        highlight=False,
    )
)
```

## 示例：类型搜索

```python
sync(
    search.search_by_type(
        "周杰伦",
        search_type=search.SearchType.SINGER,
        page=1,
        highlight=False,
    )
)
```

## 示例：快速搜索

```python
sync(search.quick_search("周杰伦"))
```
