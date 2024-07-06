# Module singer.py

```python
from qqmusic_api import Singer
```

歌手操作类

## class AreaType

**Extends:** enum.Enum

地区

+ ALL: 全部
+ CHINA: 内地
+ TAIWAN: 台湾
+ AMERICA: 美国
+ EUROPE: 欧美
+ JAPAN: 日本
+ KOREA: 韩国

## class GenreType

**Extends:** enum.Enum

风格

+ ALL: 全部
+ POP: 流行
+ RAP: 说唱
+ CHINESE_STYLE: 国风
+ ROCK: 摇滚
+ ELECTRONIC: 电子
+ FOLK: 民谣
+ R_AND_B: R&B
+ ETHNIC: 民族乐
+ LIGHT_MUSIC: 轻音乐
+ JAZZ: 爵士
+ CLASSICAL: 古典
+ COUNTRY: 乡村
+ BLUES: 蓝调

## class SexType

**Extends:** enum.Enum

性别

+ ALL: 全部
+ MALE: 男
+ FEMALE: 女
+ GROUP: 组合

## class TabType

**Extends:** enum.Enum

Tab 类型

+ WIKI: wiki
+ ALBUM: 专辑
+ COMPOSER: 作曲
+ LYRICIST: 作词
+ PRODUCER: 制作人
+ ARRANGER: 编曲
+ MUSICIAN: 乐手
+ SONG: 歌曲
+ VIDEO: 视频

## async def get_singer_list()

获取歌手列表

| name | type | description |
| - | - | - |
| area | AreaType | 地区. Defaults to AreaType.ALL |
| sex | SexType | 性别. Defaults to SexType.ALL |
| genre | GenreType | 风格. Defaults to GenreType.ALL |

**Returns:** list: 歌手列表

## class Singer

歌手类

### \_\_init\_\_()

| name | type | description |
| - | - | - |
| mid | str | 歌手 mid |

### async def get_info()

获取歌手信息

**Returns:** dict: 歌手信息

### async def get_fans_num()

获取歌手粉丝数

**Returns:** int: 粉丝数

### async def get_tab_detail()

获取歌手 Tab 详细信息

| name | type | description |
| - | - | - |
| tab_type | TabType | Tab 类型 |
| page | int | 页码 |
| num | int | 返回数量 |

**Returns:** list: Tab 详细信息

### async def get_wiki()

获取歌手WiKi

**Returns:** dict: 歌手WiKi

### async def get_song()

获取歌手歌曲

| name | type | description |
| - | - | - |
| t | TabType | Tab 类型. Defaults to TabType.SONG |
| page | int | 页码. Defaults to 1 |
| num | int | 返回数量. Defaults to 100 |

**Returns:** list[Song]: `Song` 列表
