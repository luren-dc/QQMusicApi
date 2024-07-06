# Module album.py

```python
from qqmusic_api import album
```

专辑操作类

## class Album

专辑类

### \_\_init\_\_()

| name | type | description |
| - | - | - |
| mid | str | 专辑 mid |

### async def get_detail()

获取专辑详细信息

**Returns:** dict: 专辑详细信息

### async def get_song()

获取专辑歌曲

**Returns:** list[Song]: 歌曲列表
