# Module top.py

```python
from qqmusic_api import top
```

排行榜操作类

## async def get_top_category()

获取所有排行榜

| name | type | description |
| - | - | - |
| show_detail | bool | 是否显示详情(包括介绍，前三歌曲). Defaults to False |

**Returns:** list[dict]: 排行榜信息

## class Top

排行榜类

### \_\_init\_\_()

| name | type | description |
| - | - | - |
| id | int | 排行榜 ID |
| period | str | 排行榜时间 |

### async def get_detail()

获取排行榜详细信息

**Returns:** dict: 排行榜信息

### async def get_song()

获取排行榜歌曲

**Returns:** list[Song]: 排行榜歌曲
