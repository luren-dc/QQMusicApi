# Module mv.py

```python
from qqmusic_api import mv
```

MV 操作类

## class MV

MV 类

### \_\_init\_\_()

| name | type | description |
| - | - | - |
| vid | str | MV vid |

### async def get_detail()

获取 MV 详细信息

**Returns:** dict: 视频信息

### async def get_related_song()

获取 MV 相关歌曲

**Returns:** list[dict]: 歌曲基本信息

### async def get_url()

获取 MV 播放链接

**Returns:** dict: 视频播放链接

## async def get_mv_urls(vid: list[str])

获取 MV 播放链接

| name | type | description |
| - | - | - |
| vid | list[str] | 视频 vid 列表 |

**Returns:** dict: 视频播放链接
