"""歌曲相关 API"""

import asyncio
import random
from enum import Enum
from typing import Literal, Optional

from .utils.credential import Credential
from .utils.model import ProducerObject, RelatedMV, RelatedPlaylist, RelatedSheet, SongDetail, SongInfo, SongLabel
from .utils.network import Api
from .utils.utils import get_api

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
    def s(self) -> str:
        """获取文件类型标识符"""
        return self.__start_code

    @property
    def e(self) -> str:
        """获取文件类型后缀名"""
        return self.__extension


# 歌曲文件链接类型
UrlType = Literal["play_url", "download_url"]


class Song:
    """歌曲类"""

    def __init__(
        self,
        mid: Optional[str] = None,
        id: Optional[int] = None,
    ) -> None:
        """/// admonition | 注意
        歌曲 mid 和 id，两者至少提供一个
        ///

        Args:
            mid: 歌曲 mid
            id: 歌曲 id
        """
        if mid is None and id is None:
            raise ValueError("mid or id must be provided")
        self.mid = mid or ""
        self.id = id or 0
        self._info: Optional[SongInfo] = None

    async def get_mid(self) -> str:
        """获取歌曲 mid

        Returns:
            mid
        """
        if not self.mid:
            self.mid = (await self.get_info()).mid
        return str(self.mid)

    async def get_id(self) -> int:
        """获取歌曲 id

        Returns:
            id
        """
        if not self.id:
            self.id = (await self.get_info()).id
        return int(self.id)

    async def get_info(self) -> SongInfo:
        """获取歌曲信息

        Returns:
            歌曲信息
        """
        if self._info:
            return self._info
        if self.mid is not None:
            self._info = (await query_by_mid([self.mid]))[0]
            return self._info
        elif self.id is not None:
            self._info = (await query_by_id([self.id]))[0]
            return self._info
        raise ValueError("mid or id must be provided")

    async def get_detail(self) -> SongDetail:
        """获取歌曲详细信息

        Returns:
            未经过处理的歌曲详细信息
        """
        data = await Api(**API["detail"]).update_params(song_mid=self.mid, song_id=self.id).result
        data.update(data.pop("info"))
        return SongDetail(**data)

    async def get_similar_song(self) -> list[SongInfo]:
        """获取歌曲相似歌曲

        Returns:
            歌曲信息
        """
        res = await Api(**API["similar"]).update_params(songid=await self.get_id()).result
        return [SongInfo(**song["track"]) for song in res["vecSong"]]

    async def get_labels(self) -> list[SongLabel]:
        """获取歌曲标签

        Returns:
            标签信息
        """
        data = (await Api(**API["labels"]).update_params(songid=await self.get_id()).result)["labels"]
        return [SongLabel(**tag) for tag in data]

    async def get_related_songlist(self) -> list[RelatedPlaylist]:
        """获取歌曲相关歌单

        Returns:
            歌单信息
        """
        data = (await Api(**API["playlist"]).update_params(songid=await self.get_id()).result)["vecPlaylist"]
        return [RelatedPlaylist(**playlist) for playlist in data]

    async def get_related_mv(self) -> list[RelatedMV]:
        """获取歌曲相关MV

        Returns:
            MV信息
        """
        data = (await Api(**API["mv"]).update_params(songtype=1, songid=str(await self.get_id())).result)["list"]
        return [RelatedMV(**mv) for mv in data]

    async def get_other_version(self) -> list[SongInfo]:
        """获取歌曲其他版本

        Returns:
            歌曲信息
        """
        res = await Api(**API["other"]).update_params(songmid=self.mid, songid=self.id).result
        return [SongInfo(**song) for song in res["versionList"]]

    async def get_sheet(self) -> list[RelatedSheet]:
        """获取歌曲相关曲谱

        Returns:
            曲谱信息
        """
        data = (await Api(**API["sheet"]).update_params(songmid=await self.get_mid(), scoreType=-1).result)["result"]
        return [RelatedSheet(**sheet) for sheet in data]

    async def get_producer(self) -> list[ProducerObject]:
        """获取歌曲制作信息

        Returns:
            人员信息
        """
        data = (await Api(**API["producer"]).update_params(songmid=self.mid, songid=self.id).result)["Lst"]
        return [ProducerObject(**producer) for producer in data]

    async def get_url(
        self,
        file_type: SongFileType = SongFileType.MP3_128,
        url_type: UrlType = "play_url",
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
        return await get_song_urls([await self.get_mid()], file_type, url_type, credential)


async def query_by_id(id: list[int]) -> list[SongInfo]:
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
    return [SongInfo(**song) for song in tracks]


async def query_by_mid(mid: list[str]) -> list[SongInfo]:
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
    return [SongInfo(**song) for song in tracks]


async def get_song_urls(
    mid: list[str],
    file_type: SongFileType = SongFileType.MP3_128,
    url_type: UrlType = "play_url",
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
    domain = "https://isure.stream.qqmusic.qq.com/" if url_type == "play_url" else "https://dl.stream.qqmusic.qq.com/"
    api = Api(**API[url_type], credential=credential)
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
