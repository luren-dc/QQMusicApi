"""歌曲相关 API"""

import asyncio
from enum import Enum
from typing import Optional, Union, overload

from .utils.common import get_api, get_guid
from .utils.credential import Credential
from .utils.network import Api

API = get_api("song")


async def query_song(value: Union[list[str], list[int]]) -> list[dict]:
    """根据 id 或 mid 获取歌曲信息

    Args:
        value: 歌曲 id 或 mid 列表

    Returns:
        歌曲信息
    """
    if not value:
        return []

    param = {
        "types": [0 for _ in range(len(value))],
        "modify_stamp": [0 for _ in range(len(value))],
        "ctx": 0,
        "client": 1,
    }
    if isinstance(value[0], int):
        param["ids"] = value
    else:
        param["mids"] = value
    res = await Api(**API["query"]).update_params(**param).result
    return res["tracks"]


class BaseSongFileType(Enum):
    """基础歌曲文件类型"""

    def __init__(self, start_code: str, extension: str):
        self.__start_code = start_code
        self.__extension = extension

    @property
    def s(self) -> str:
        """歌曲文件类型"""
        return self.__start_code

    @property
    def e(self) -> str:
        """歌曲文件扩展名"""
        return self.__extension


class SongFileType(BaseSongFileType):
    """歌曲文件类型

    + MASTER:   臻品母带2.0,24Bit 192kHz,size_new[0]
    + ATMOS_2:  臻品全景声2.0,16Bit 44.1kHz,size_new[1]
    + ATMOS_51: 臻品音质2.0,16Bit 44.1kHz,size_new[2]
    + FLAC:     flac 格式,16Bit 44.1kHz~24Bit 48kHz,size_flac
    + OGG_640:  ogg 格式,640kbps,size_new[5]
    + OGG_320:  ogg 格式,320kbps,size_new[3]
    + OGG_192:  ogg 格式,192kbps,size_192ogg
    + OGG_96:   ogg 格式,96kbps,size_96ogg
    + MP3_320:  mp3 格式,320kbps,size_320mp3
    + MP3_128:  mp3 格式,128kbps,size_128mp3
    + ACC_192:  m4a 格式,192kbps,size_192aac
    + ACC_96:   m4a 格式,96kbps,size_96aac
    + ACC_48:   m4a 格式,48kbps,size_48aac
    """

    MASTER = ("AI00", ".flac")
    ATMOS_2 = ("Q000", ".flac")
    ATMOS_51 = ("Q001", ".flac")
    FLAC = ("F000", ".flac")
    OGG_640 = ("O801", ".ogg")
    OGG_320 = ("O800", ".ogg")
    OGG_192 = ("O600", ".ogg")
    OGG_96 = ("O400", ".ogg")
    MP3_320 = ("M800", ".mp3")
    MP3_128 = ("M500", ".mp3")
    ACC_192 = ("C600", ".m4a")
    ACC_96 = ("C400", ".m4a")
    ACC_48 = ("C200", ".m4a")


class EncryptedSongFileType(BaseSongFileType):
    """加密歌曲文件类型

    + MASTER:   臻品母带2.0,24Bit 192kHz,size_new[0]
    + ATMOS_2:  臻品全景声2.0,16Bit 44.1kHz,size_new[1]
    + ATMOS_51: 臻品音质2.0,16Bit 44.1kHz,size_new[2]
    + FLAC:     mflac 格式,16Bit 44.1kHz~24Bit 48kHz,size_flac
    + OGG_640:  mgg 格式,640kbps,size_new[5]
    + OGG_320:  mgg 格式,320kbps,size_new[3]
    + OGG_192:  mgg 格式,192kbps,size_192ogg
    + OGG_96:   mgg 格式,96kbps,size_96ogg
    """

    MASTER = ("AIM0", ".mflac")
    ATMOS_2 = ("Q0M0", ".mflac")
    ATMOS_51 = ("Q0M1", ".mflac")
    FLAC = ("F0M0", ".mflac")
    OGG_640 = ("O801", ".mgg")
    OGG_320 = ("O800", ".mgg")
    OGG_192 = ("O6M0", ".mgg")
    OGG_96 = ("O4M0", ".mgg")


@overload
async def get_song_urls(
    mid: list[str],
    file_type: SongFileType = SongFileType.MP3_128,
    credential: Optional[Credential] = None,
) -> dict[str, str]: ...


@overload
async def get_song_urls(
    mid: list[str],
    file_type: EncryptedSongFileType,
    credential: Optional[Credential] = None,
) -> dict[str, tuple[str, str]]: ...


async def get_song_urls(
    mid: list[str],
    file_type: Union[EncryptedSongFileType, SongFileType] = SongFileType.MP3_128,
    credential: Optional[Credential] = None,
) -> Union[dict[str, str], dict[str, tuple[str, str]]]:
    """获取歌曲文件链接

    Tips:
        `ekey` 用于解密加密歌曲

    Args:
        mid:        歌曲 mid
        file_type:  歌曲文件类型
        credential: 账号凭证

    Returns:
        SongFileType: `{mid: url}`
        EncryptedSongFileType: `{mid: (url, ekey)}`
    """
    encrypted = isinstance(file_type, EncryptedSongFileType)
    # 分割 id,单次最大请求100
    mid_list = [mid[i : i + 100] for i in range(0, len(mid), 100)]
    # 选择文件域名
    domain = "https://isure.stream.qqmusic.qq.com/"
    api_data = API["play_url"] if not encrypted else API["evkey"]
    api = Api(**api_data, credential=credential or Credential())
    urls = {}

    async def get_song_url(mid):
        # 构造请求参数
        file_name = [f"{file_type.s}{_}{_}{file_type.e}" for _ in mid]
        param = {
            "filename": file_name,
            "guid": get_guid(),
            "songmid": mid,
            "songtype": [0 for _ in range(len(mid))],
        }

        res = await api.update_params(**param).result
        data = res["midurlinfo"]
        for info in data:
            song_url = domain + info["wifiurl"] if info["wifiurl"] else ""
            if not encrypted:
                urls[info["songmid"]] = song_url
            else:
                urls[info["songmid"]] = (song_url, info["ekey"])

    await asyncio.gather(*[asyncio.create_task(get_song_url(mid)) for mid in mid_list])
    return urls


async def get_try_url(mid: str, vs: str) -> str:
    """获取试听文件链接

    Tips:
        使用 `size_try` 字段判断是否存在试听文件
        参数 `vs` 请传入歌曲信息 `vs` 字段第一个

    Args:
        mid: 歌曲 mid
        vs:  歌曲 vs

    Returns:
        试听文件链接
    """
    res = await (
        Api(**API["play_url"])
        .update_params(
            filename=[f"RS02{vs}.mp3"],
            guid=get_guid(),
            songmid=[mid],
            songtype=[1],
        )
        .result
    )
    if url := res["midurlinfo"][0]["wifiurl"]:
        return f"https://isure.stream.qqmusic.qq.com/{url}"
    return ""


class Song:
    """歌曲类

    Attributes:
        mid: 歌曲 mid
        id:  歌曲 id
    """

    def __init__(
        self,
        *,
        mid: Optional[str] = None,
        id: Optional[int] = None,
    ):
        """初始化歌曲类

        Note:
            歌曲 mid 和 id,两者至少提供一个

        Args:
            mid: 歌曲 mid
            id:  歌曲 id
        """
        if mid is None and id is None:
            raise ValueError("mid or id must be provided")
        self.mid = mid or ""
        self.id = id or 0
        self._info: Optional[dict] = None

    async def get_mid(self) -> str:
        """获取歌曲 mid

        Returns:
            歌曲 mid
        """
        if not self.mid:
            if self.id:
                self.mid = (await query_song([self.id]))[0]["mid"]
        return self.mid

    async def get_id(self) -> int:
        """获取歌曲 id

        Returns:
            歌曲 id
        """
        if not self.id:
            if self.mid:
                self.id = (await query_song([self.mid]))[0]["id"]
        return self.id

    async def get_info(self) -> dict:
        """获取歌曲信息

        Returns:
            歌曲信息
        """
        if not self._info:
            if self.mid:
                self._info = (await query_song([self.mid]))[0]
            else:
                self._info = (await query_song([self.id]))[0]
        return self._info

    async def get_detail(self) -> dict:
        """获取歌曲详细信息

        Returns:
            详细信息
        """
        return await Api(**API["detail"]).update_params(song_mid=self.mid, song_id=self.id).result

    async def get_similar_song(self) -> list[dict]:
        """获取歌曲相似歌曲

        Returns:
            歌曲信息
        """
        return (await Api(**API["similar"]).update_params(songid=await self.get_id()).result)["vecSong"]

    async def get_labels(self) -> list[dict]:
        """获取歌曲标签

        Returns:
            标签信息
        """
        return (await Api(**API["labels"]).update_params(songid=await self.get_id()).result)["labels"]

    async def get_related_songlist(self) -> list[dict]:
        """获取歌曲相关歌单

        Returns:
            歌单信息
        """
        return (await Api(**API["playlist"]).update_params(songid=await self.get_id()).result)["vecPlaylist"]

    async def get_related_mv(self) -> list[dict]:
        """获取歌曲相关MV

        Returns:
            MV信息
        """
        return (
            await Api(**API["mv"])
            .update_params(
                songid=str(await self.get_id()),
                songtype=1,
                lastmvid=0,
            )
            .result
        )["list"]

    async def get_other_version(self) -> list[dict]:
        """获取歌曲其他版本

        Returns:
            歌曲信息
        """
        return (await Api(**API["other"]).update_params(songid=self.id, songmid=self.mid).result)["versionList"]

    async def get_sheet(self) -> list[dict]:
        """获取歌曲相关曲谱

        Returns:
            曲谱信息
        """
        return (await Api(**API["sheet"]).update_params(songmid=await self.get_mid(), scoreType=-1).result)["result"]

    async def get_producer(self) -> list[dict]:
        """获取歌曲制作信息

        Returns:
            人员信息
        """
        return (await Api(**API["producer"]).update_params(songid=self.id, songmid=self.mid).result)["Lst"]

    @overload
    async def get_url(
        self,
        file_type: SongFileType = SongFileType.MP3_128,
        credential: Optional[Credential] = None,
    ) -> str: ...

    @overload
    async def get_url(
        self,
        file_type: EncryptedSongFileType,
        credential: Optional[Credential] = None,
    ) -> tuple[str, str]: ...

    async def get_url(
        self,
        file_type: Union[SongFileType, EncryptedSongFileType] = SongFileType.MP3_128,
        credential: Optional[Credential] = None,
    ) -> Union[str, tuple[str, str]]:
        """获取歌曲文件链接

        Tips:
            `ekey` 用于解密加密歌曲

        Args:
            file_type:  歌曲文件类型
            credential: 账号凭证

        Returns:
            SongFileType: 歌曲文件链接
            EncryptedSongFileType: (加密文件链接, ekey)
        """
        return (await get_song_urls([await self.get_mid()], file_type, credential))[self.mid]

    async def get_try_url(self) -> str:
        """获取试听文件链接

        Returns:
            试听文件链接
        """
        vs = (await self.get_info())["vs"][0]
        if not vs:
            return ""
        return await get_try_url(self.mid, vs)
