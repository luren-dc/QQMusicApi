from enum import Enum
from typing import Optional

from ..exceptions import ArgsException
from ..utils.common import get_api, parse_song_info
from ..utils.credential import Credential
from ..utils.network import Api

API = get_api("song")


class SongFileType(Enum):
    """
    歌曲文件类型
    + NEW_0:   unkown
    + NEW_1:   unkown
    + NEW_2:   unkown
    + FLAC:    无损音频压缩格式
    + OGG_192: OGG 格式，192kbps
    + OGG_96:  OGG 格式，96kbps
    + MP3_320: MP3 格式，320kbps
    + MP3_128: MP3 格式，128kbps
    + ACC_192: AAC 格式，192kbps
    + ACC_96:  AAC 格式，96kbps
    + ACC_48:  AAC 格式，48kbps
    + TRY:     试听文件
    """

    NEW_0 = ("AI00", ".flac")
    NEW_1 = ("Q000", ".flac")
    NEW_2 = ("Q001", ".flac")
    FLAC = ("F000", ".flac")
    OGG_192 = ("O600", ".ogg")
    OGG_96 = ("O400", ".ogg")
    MP3_320 = ("M800", ".mp3")
    MP3_128 = ("M500", ".mp3")
    ACC_192 = ("C600", ".m4a")
    ACC_96 = ("C400", ".m4a")
    ACC_48 = ("C200", ".m4a")
    TRY = ("RS02", ".mp3")

    def __init__(self, start_code: str, extension: str):
        self.start_code = start_code
        self.extension = extension

    @property
    def s(self) -> str:
        return self.start_code

    @property
    def e(self) -> str:
        return self.extension


class UrlType(Enum):
    """
    歌曲文件链接类型
    + PLAY:     播放链接
    + DOWNLOAD: 下载链接
    """

    PLAY = 0
    DOWNLOAD = 1


class Song:
    """
    歌曲类
    """

    def __init__(
        self,
        mid: Optional[str] = None,
        id: Optional[int] = None,
        credential: Optional[Credential] = None,
    ):
        """
        Args:
            mid:        歌曲 mid. 歌曲 id 和歌曲 mid 必须提供其中之一,优先使用 mid
            id:         歌曲 id. 歌曲 id 和歌曲 mid 必须提供其中之一,优先使用 mid
            credential: Credential 类. Defaluts to None
        """
        # ID 检查
        if mid is not None:
            self.mid = mid
        elif id is not None:
            self.id = id
        else:
            # 未提供任一 ID
            raise ArgsException("请至少提供 mid 和 id 中的其中一个参数。")

        self.credential = Credential() if credential is None else credential
        self._info: Optional[dict] = None

    async def get_detail(self):
        pass

    async def get_similar_song(self):
        pass

    async def get_labels(self):
        pass

    async def get_related_playlist(self):
        pass

    async def get_related_mv(self):
        pass

    async def get_other_version(self):
        pass

    async def get_sheet(self):
        pass

    async def get_producer(self):
        pass

    async def get_url(
        self,
        file_type: SongFileType = SongFileType.MP3_128,
        url_type: UrlType = UrlType.PLAY,
    ):
        pass


async def query_by_id(id: list[int]) -> list[dict]:
    """
    根据 mid 获取歌曲信息

    Args:
        mid: 歌曲 mid 列表

    Returns:
        list[dict]: 歌曲信息
    """
    if not all(isinstance(item, int) for item in id):
        raise ArgsException("请传入正确的参数")
    param = {
        "ids": id,
        "mids": [],
        "types": [0 for i in range(len(id))],
        "modify_stamp": [0 for i in range(len(id))],
        "ctx": 0,
        "client": 1,
    }
    res = await Api(**API["song"]["query"]).update_params(**param).result
    tracks = res["tracks"]
    return [parse_song_info(song) for song in tracks]


async def query_by_mid(mid: list[str]) -> list[dict]:
    """
    根据 mid 获取歌曲信息

    Args:
        mid: 歌曲 mid 列表

    Returns:
        list[dict]: 歌曲信息
    """
    if not all(isinstance(item, str) for item in mid):
        raise ArgsException("请传入正确的参数")
    param = {
        "ids": [],
        "mids": mid,
        "types": [0 for i in range(len(mid))],
        "modify_stamp": [0 for i in range(len(mid))],
        "ctx": 0,
        "client": 1,
    }
    res = await Api(**API["song"]["query"]).update_params(**param).result
    tracks = res["tracks"]
    return [parse_song_info(song) for song in tracks]


async def urls(
    media_mid: list[str],
    mid: list[str],
    file_type: SongFileType = SongFileType.MP3_128,
    url_type: UrlType = UrlType.PLAY,
):
    """
    获取歌曲文件链接

    Args:
        media_mid: 媒体资源 id. media_mid 和 mid 必须提供其中之一,优先使用 media_mid
        mid:       歌曲 mid. media_mid 和 mid 必须提供其中之一,优先使用 media_mid
        file_type: 歌曲文件类型. Defaults to SongFileType.MP3_128
        url_type:  歌曲链接类型. Defaults to UrlType.PLAY
    """
