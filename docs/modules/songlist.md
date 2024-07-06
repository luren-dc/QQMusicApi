# Module songlist.py

```python
from qqmusic_api import songlist
```

歌单操作类

## class Songlist

歌单类

### \_\_init\_\_()

| name | type | description |
| - | - | - |
| id | int | 歌单 ID |

### async def get_detail()

获取歌单详细信息

**Returns:** dict: 歌单信息

### async def get_song()

获取歌单歌曲

**Returns:** list[Song]: 歌单歌曲

### async def get_song_tag()

获取歌单歌曲标签

**Returns:** list[dict]: 歌单歌曲标签

### async def get_song_mid()

获取歌单歌曲全部 mid

**Returns:** list[dict]: 歌单歌曲 mid
