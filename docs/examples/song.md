# 歌曲

## 获取歌曲信息

```python
import asyncio

from qqmusic_api import song

song = song.Song(mid="0016aXcd24qSC")
# song.Song(id=457240977)

mid = asyncio.run(song.get_id())
id = asyncio.run(song.get_mid())

# 获取基本信息
info = asyncio.run(song.get_info())

# 获取详细信息
detail = asyncio.run(song.get_detail())
```

## 下载歌曲

```python
--8<-- "examples/download_song.py"
```
