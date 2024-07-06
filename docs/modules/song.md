# Module song.py

```python
from qqmusic_api import song
```

歌曲操作类

## class SongFileType

**Extends:** enum.Enum

歌曲文件类型

+ NEW_0: 臻品母带2.0
+ NEW_1: 臻品全景声
+ NEW_2: 臻品音质2.0
+ FLAC: 无损音频压缩格式
+ OGG_192: OGG 格式，192kbps
+ OGG_96: OGG 格式，96kbps
+ MP3_320: MP3 格式，320kbps
+ MP3_128: MP3 格式，128kbps
+ ACC_192: AAC 格式，192kbps
+ ACC_96: AAC 格式，96kbps
+ ACC_48: AAC 格式，48kbps
+ TRY: 试听文件

## class UrlType

**Extends:** enum.Enum

歌曲文件链接类型

+ PLAY: 播放链接
+ DOWNLOAD: 下载链接

## class Song

?> 注意，同时存在 mid 和 id 的参数，两者至少提供一个。

歌曲类

### \_\_init\_\_()

| name | type | description |
| - | - | - |
| mid | Optional[str] | 歌曲 mid. 歌曲 id 和歌曲 mid 必须提供其中之一 |
| id | Optional[int] | 歌曲 id. 歌曲 id 和歌曲 mid 必须提供其中之一 |

### async def get_info()

获取歌曲基本信息

**Returns:** dict: 基本信息

### async def get_singer()

获取歌曲歌手

**Returns:** Singer: 歌手

### async def get_album()

获取歌曲专辑

**Returns:** Album: 专辑

### async def get_detail()

获取歌曲详细信息

**Returns:** dict: 详细信息

### async def get_similar_song()

获取歌曲相似歌曲

**Returns:** list[dict]: 歌曲信息

### async def get_labels()

获取歌曲标签

**Returns:** list[dict]: 标签信息

### async def get_related_songlist()

获取歌曲相关歌单

**Returns:** list[dict]: 歌单信息

### async def get_related_mv()

获取歌曲相关MV

**Returns:** list[dict]: MV信息

### async def get_other_version()

获取歌曲其他版本

**Returns:** list[dict]: 歌曲信息

### async def get_sheet()

获取歌曲相关曲谱

**Returns:** list[dict]: 曲谱信息

### async def get_producer()

获取歌曲制作信息

**Returns:** list[dict]: 人员信息

### async def get_url()

获取歌曲文件链接

| name | type | description |
| - | - | - |
| file_type | SongFileType | 歌曲文件类型. Defaults to SongFileType.MP3_128 |
| url_type | UrlType | 歌曲链接类型. Defaults to UrlType.PLAY |
| credential | Optional[Credential] | 账号凭证. Defaults to None |

**Returns:** dict[str, str]: 链接字典

### async def get_file_size()

获取歌曲文件大小

| name | type | description |
| - | - | - |
| file_type | Optional[SongFileType] | 指定文件类型. Defaults to None |

**Returns:** dict: 文件大小

## async def query_by_id()

根据 id 获取歌曲信息

| name | type | description |
| - | - | - |
| id | list[int] | 歌曲 id 列表 |

**Returns:** list[dict]: 歌曲信息

## async def query_by_mid()

根据 mid 获取歌曲信息

| name | type | description |
| - | - | - |
| mid | list[str] | 歌曲 mid 列表 |

**Returns:** list[dict]: 歌曲信息

## async def get_song_urls()

获取歌曲文件链接

| name | type | description |
| - | - | - |
| mid | list[str] | 歌曲 mid |
| file_type | SongFileType | 歌曲文件类型. Defaults to SongFileType.MP3_128 |
| url_type | UrlType | 歌曲链接类型. Defaults to UrlType.PLAY |
| credential | Optional[Credential] | Credential 类. Defaults to None |

**Returns:** dict[str, str]: 链接字典
