# Module search.py

```python
from qqmusic_api import search
```

搜索操作类

## class SearchType

**Extends:** enum.Enum

搜索类型

+ SONG: 歌曲
+ SINGER: 歌手
+ ALBUM: 专辑
+ SONGLIST: 歌单
+ MV: MV
+ LYRIC: 歌词
+ USER: 用户
+ AUDIO_ALBUM: 节目专辑
+ AUDIO: 节目

## async def hotkey()

获取热搜词

**Returns:** list[dict]: 热搜词列表，k为热搜词，n为搜索量

## async def complete()

搜索词补全

| name | type | description |
| - | - | - |
| keyword | str | 关键词 |
| highlight | bool | 是否高亮关键词. Defaults to False |

**Returns:** list[str]: 补全结果

## async def quick_search()

快速搜索

| name | type | description |
| - | - | - |
| keyword | str | 关键词 |

**Returns:** dict: 包含专辑，歌手，歌曲的简略信息

## async def general_search()

综合搜索

| name | type | description |
| - | - | - |
| keyword | str | 关键词 |
| page | int | 页码. Defaults to 1 |
| highlight | bool | 是否高亮关键词. Defaults to False |

**Returns:** dict: 包含直接结果，歌曲，歌手，专辑，歌单，mv等.

## async def search_by_type()

搜索

| name | type | description |
| - | - | - |
| keyword | str | 关键词 |
| search_type | SearchType | 搜索类型. Defaults to SearchType.SONG |
| num | int | 返回数量. Defaults to 10 |
| page | int | 页码. Defaults to 1 |
| selectors | dict | 选择器. Defaults to {} |
| highlight | bool | 是否高亮关键词. Defaults to False |

**Returns:** list[Song]: 搜索结果
