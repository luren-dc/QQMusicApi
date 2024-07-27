"""歌曲相关 API"""

import asyncio
import random
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .album import Album
    from .singer import Singer

from .utils.credential import Credential
from .utils.network import Api
from .utils.utils import get_api, parse_song_info

API = get_api("song")


class SongFileType(Enum):
    """歌曲文件类型

    + NEW_0:   臻品母带2.0
    + NEW_1:   臻品全景声
    + NEW_2:   臻品音质2.0
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
        self.__start_code = start_code
        self.__extension = extension

    @property
    def s(self) -> str:  # noqa : D102
        return self.__start_code

    @property
    def e(self) -> str:  # noqa: D102
        return self.__extension


class UrlType(Enum):
    """歌曲文件链接类型

    + PLAY:     播放链接
    + DOWNLOAD: 下载链接
    """

    PLAY = "play_url"
    DOWNLOAD = "download_url"


class Song:
    """歌曲类

    Attributes:
        mid: 歌曲 mid
        id: 歌曲 id
    """

    def __init__(
        self,
        mid: Optional[str] = None,
        id: Optional[int] = None,
    ):
        """/// admonition | 注意
        歌曲 mid 和 id，两者至少提供一个
        ///

        Args:
            mid: 歌曲 mid
            id: 歌曲 id
        """
        # ID 检查
        if mid is None and id is None:
            raise TypeError("mid or id must be provided")
        self._mid = mid
        self._id = id
        self._info: Optional[dict] = None

    @classmethod
    def from_dict(cls, info: dict) -> "Song":
        """从字典新建 Song

        Args:
            info: 歌曲字典

        Returns:
            歌曲类
        """
        info = parse_song_info(info)
        s = cls(id=info["info"]["id"], mid=info["info"]["mid"])
        s._info = info
        return s

    @classmethod
    def from_list(cls, data: list[dict]) -> list["Song"]:
        """从列表新建 Song

        Args:
            data: 歌曲列表

        Returns:
            歌曲列表
        """
        return [cls.from_dict(info) for info in data]

    async def __get_info(self) -> dict:
        """获取歌曲必要信息"""
        if not self._info:
            if self._mid:
                self._info = (await query_by_mid([self._mid]))[0]
            elif self._id:
                self._info = (await query_by_id([self._id]))[0]
        return self._info  # type: ignore

    @property
    async def mid(self) -> str:
        """获取歌曲 mid

        Returns:
            mid
        """
        if not self._mid:
            self._mid = (await self.__get_info())["info"]["mid"]
        return str(self._mid)

    @property
    async def id(self) -> int:
        """获取歌曲 id

        Returns:
            id
        """
        if not self._id:
            self._id = (await self.__get_info())["info"]["id"]
        return int(self._id)  # type: ignore

    def __repr__(self) -> str:
        return f"Song(mid={self._mid}, id={self._id})"

    def __str__(self) -> str:
        if self._info:
            return str(self._info)
        return self.__repr__()

    async def __prepare_param(self, is_mid: bool = False, is_id: bool = False) -> dict:
        """准备请求参数

        Args:
            is_mid: 是否强制使用 mid. Defaults to False
            is_id:  是否强制使用 id. Defaults to False

        Returns:
            请求参数
        """
        if is_mid:
            return {"songmid": await self.mid}
        if is_id:
            return {"songid": await self.id}
        if self._mid:
            return {"songmid": self._mid}
        if self._id:
            return {"songid": self._id}
        return {}

    async def get_info(self) -> dict:
        """获取歌曲基本信息

        Returns:
            基本信息
        """
        return (await self.__get_info())["info"]

    async def get_singer(self) -> "Singer":
        """获取歌曲歌手

        Returns:
            歌手
        """
        from .singer import Singer

        return Singer((await self.__get_info())["singer"]["mid"])

    async def get_album(self) -> "Album":
        """获取歌曲专辑

        Returns:
            专辑
        """
        from .album import Album

        return Album((await self.__get_info())["album"]["mid"])

    async def get_detail(self) -> dict:
        """获取歌曲详细信息

        Returns:
            详细信息
        """
        param = await self.__prepare_param()
        if "songmid" in param:
            param["song_mid"] = param.pop("songmid")
        if "songid" in param:
            param["song_id"] = param.pop("songid")
        return await Api(**API["detail"]).update_params(**param).result

    async def get_similar_song(self) -> list[dict]:
        """获取歌曲相似歌曲

        Returns:
            歌曲信息
        """
        param = await self.__prepare_param(is_id=True)
        res = await Api(**API["similar"]).update_params(**param).result
        return [parse_song_info(song["track"]) for song in res["vecSong"]]

    async def get_labels(self) -> list[dict]:
        """获取歌曲标签

        Returns:
            标签信息
        """
        param = await self.__prepare_param(is_id=True)
        return (await Api(**API["labels"]).update_params(**param).result)["labels"]

    async def get_related_songlist(self) -> list[dict]:
        """获取歌曲相关歌单

        Returns:
            歌单信息
        """
        param = await self.__prepare_param(is_id=True)
        return (await Api(**API["playlist"]).update_params(**param).result)["vecPlaylist"]

    async def get_related_mv(self) -> list[dict]:
        """获取歌曲相关MV

        Returns:
            MV信息
        """
        param = await self.__prepare_param()
        return (await Api(**API["mv"]).update_params(**param).result)["list"]

    async def get_other_version(self) -> list[dict]:
        """获取歌曲其他版本

        Returns:
            歌曲信息
        """
        param = await self.__prepare_param()
        res = await Api(**API["other"]).update_params(**param).result
        return [parse_song_info(song) for song in res["versionList"]]

    async def get_sheet(self) -> list[dict]:
        """获取歌曲相关曲谱

        Returns:
            曲谱信息
        """
        param = await self.__prepare_param(is_mid=True)
        param["scoreType"] = -1
        return (await Api(**API["sheet"]).update_params(**param).result)["result"]

    async def get_producer(self) -> list[dict]:
        """获取歌曲制作信息

        Returns:
            人员信息
        """
        param = await self.__prepare_param()
        return (await Api(**API["producer"]).update_params(**param).result)["Lst"]

    async def get_url(
        self,
        file_type: SongFileType = SongFileType.MP3_128,
        url_type: UrlType = UrlType.PLAY,
        credential: Optional[Credential] = None,
    ) -> dict[str, str]:
        """获取歌曲文件链接

        Args:
            file_type:  歌曲文件类型. Defaults to SongFileType.MP3_128
            url_type:   歌曲链接类型. Defaults to UrlType.PLAY
            credential: 账号凭证. Defaults to None

        Returns:
            链接字典
        """
        return await get_song_urls([await self.mid], file_type, url_type, credential)

    async def get_file_size(self, file_type: Optional[SongFileType] = None) -> dict:
        """获取歌曲文件大小

        Args:
            file_type:  指定文件类型. Defaults to None

        Returns:
            文件大小
        """
        size = (await self.__get_info())["file"]
        if file_type:
            name = file_type.name.lower()
            size = {name: size[name]}
        return size


async def query_by_id(id: list[int]) -> list[dict]:
    """根据 id 获取歌曲信息

    Args:
        id: 歌曲 mid 列表

    Returns:
            歌曲信息
    """
    param = {
        "ids": id,
        "mids": [],
        "types": [0 for _ in range(len(id))],
        "modify_stamp": [0 for _ in range(len(id))],
        "ctx": 0,
        "client": 1,
    }
    res = await Api(**API["query"]).update_params(**param).result
    tracks = res["tracks"]
    return [parse_song_info(song) for song in tracks]


async def query_by_mid(mid: list[str]) -> list[dict]:
    """根据 mid 获取歌曲信息

    Args:
        mid: 歌曲 mid 列表

    Returns:
            歌曲信息
    """
    param = {
        "ids": [],
        "mids": mid,
        "types": [0 for _ in range(len(mid))],
        "modify_stamp": [0 for _ in range(len(mid))],
        "ctx": 0,
        "client": 1,
    }
    res = await Api(**API["query"]).update_params(**param).result
    tracks = res["tracks"]
    return [parse_song_info(song) for song in tracks]


async def get_song_urls(
    mid: list[str],
    file_type: SongFileType = SongFileType.MP3_128,
    url_type: UrlType = UrlType.PLAY,
    credential: Optional[Credential] = None,
) -> dict[str, str]:
    """获取歌曲文件链接

    Args:
        mid:        歌曲 mid
        file_type:  歌曲文件类型. Defaults to SongFileType.MP3_128
        url_type:   歌曲链接类型. Defaults to UrlType.PLAY
        credential: Credential 类. Defaluts to None

    Returns:
       链接字典
    """
    if credential is None:
        credential = Credential()
    # 分割 id,单次最大请求100
    mid_list = [mid[i : i + 100] for i in range(0, len(mid), 100)]
    # 选择文件域名
    domain = "https://isure.stream.qqmusic.qq.com/" if url_type == UrlType.PLAY else "https://dl.stream.qqmusic.qq.com/"
    api = Api(**API[url_type.value], credential=credential)
    urls = {}

    async def get_song_url(mid):
        # 构造请求参数
        file_name = [f"{file_type.s}{_}{_}{file_type.e}" for _ in mid]
        param = {
            "filename": file_name,
            "guid": "".join(random.choices("abcdef1234567890", k=32)),
            "songmid": mid,
            "songtype": [1 for _ in range(len(mid))],
        }

        res = await api.update_params(**param).result
        data = res["midurlinfo"]
        for info in data:
            song_url = domain + info["wifiurl"] if info["wifiurl"] else ""
            urls[info["songmid"]] = song_url

    await asyncio.gather(*[asyncio.create_task(get_song_url(mid)) for mid in mid_list])
    return urls
