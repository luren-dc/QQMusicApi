from enum import Enum
from typing import Optional

from ..exceptions import ArgsException
from ..utils.common import get_api, parse_song_info, random_string
from ..utils.credential import Credential
from ..utils.network import Api

API = get_api("song")["song"]


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

    PLAY = "play_url"
    DOWNLOAD = "download_url"


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
        if mid is None and id is None:
            raise ArgsException("请至少提供 mid 和 id 中的其中一个参数。")
        self._mid = mid
        self._id = id
        self.credential = Credential() if credential is None else credential
        self._info: Optional[dict] = None

    async def _get_info(self):
        """
        获取歌曲必要信息
        """
        if not self._info:
            if self._mid:
                self._info = (await query_by_mid([self._mid]))[0]
            elif self._id:
                self._info = (await query_by_id([self._id]))[0]
        return self._info

    @property
    async def mid(self):
        if not self._mid:
            self._mid = (await self._get_info())["info"]["mid"]
        return self._mid

    @property
    async def id(self):
        if not self._id:
            self._id = (await self._get_info())["info"]["id"]
        return self._id

    async def _prepare_param(self, is_mid: bool = False, is_id: bool = False) -> dict:
        """
        准备请求参数

        Args:
            is_mid: 是否强制使用 mid. Defaults to False
            is_id:  是否强制使用 id. Defaults to False

        Returns:
            dict: 请求参数
        """
        if is_mid and is_id:
            raise ArgsException("参数错误")
        if is_mid:
            return {"songmid": await self.mid}
        elif is_id:
            return {"songid": await self.id}
        elif self._mid:
            return {"songmid": self._mid}
        elif self._id:
            return {"songid": self._id}
        else:
            return {}

    async def get_info(self) -> dict:
        """
        获取歌曲基本信息

        Returns:
            dict: 基本信息
        """
        return await self._get_info()

    async def get_detail(self) -> dict:
        """
        获取歌曲详细信息

        Returns:
            dict: 详细信息
        """
        param = await self._prepare_param()
        if "songmid" in param:
            param["song_mid"] = param.pop("songmid")
        if "songid" in param:
            param["song_id"] = param.pop("songid")
        return await Api(**API["detail"]).update_params(**param).result  # type: ignore

    async def get_similar_song(self):
        param = await self._prepare_param(is_id=True)
        res = await Api(**API["similar"]).update_params(**param).result
        return [parse_song_info(song["track"]) for song in res["vecSong"]]

    async def get_labels(self):
        param = await self._prepare_param(is_id=True)
        return (await Api(**API["labels"]).update_params(**param).result)["labels"]

    async def get_related_playlist(self):
        param = await self._prepare_param(is_id=True)
        return (await Api(**API["playlist"]).update_params(**param).result)[
            "versionList"
        ]

    async def get_related_mv(self):
        param = await self._prepare_param()
        return (await Api(**API["mv"]).update_params(**param).result)["list"]

    async def get_other_version(self):
        param = await self._prepare_param()
        res = await Api(**API["other"]).update_params(**param).result
        return [parse_song_info(song) for song in res["versionList"]]

    async def get_sheet(self):
        param = await self._prepare_param(is_mid=True)
        param["scoreType"] = -1
        return (await Api(**API["sheet"]).update_params(**param).result)["result"]

    async def get_producer(self):
        param = await self._prepare_param()
        return (await Api(**API["producer"]).update_params(**param).result)["Lst"]

    async def get_url(
        self,
        file_type: SongFileType = SongFileType.MP3_128,
        url_type: UrlType = UrlType.PLAY,
    ) -> dict[str, str]:
        """
        获取歌曲文件链接
        注：有播放链接，不一定有下载链接

        Args:
            file_type:  歌曲文件类型. Defaults to SongFileType.MP3_128
            url_type:   歌曲链接类型. Defaults to UrlType.PLAY

        Returns:
            dict: 链接字典
        """
        return await get_urls([self.mid], file_type, url_type)

    async def get_file_size(self, file_type: Optional[SongFileType] = None) -> dict:
        """
        获取歌曲文件大小

        Args:
            file_type:  指定文件类型. Defaults to None

        Return:
            dict: 文件大小
        """
        size = (await self._get_info())["file"]
        if file_type:
            name = file_type.name.lower()
            size = {name: size[name]}
        return size


async def query_by_id(id: list[int]) -> list[dict]:
    """
    根据 mid 获取歌曲信息

    Args:
        mid: 歌曲 mid 列表

    Returns:
        list: 歌曲信息
    """
    param = {
        "ids": id,
        "mids": [],
        "types": [0 for i in range(len(id))],
        "modify_stamp": [0 for i in range(len(id))],
        "ctx": 0,
        "client": 1,
    }
    res = await Api(**API["query"]).update_params(**param).result
    tracks = res["tracks"]
    return [parse_song_info(song) for song in tracks]


async def query_by_mid(mid: list[str]) -> list[dict]:
    """
    根据 mid 获取歌曲信息

    Args:
        mid: 歌曲 mid 列表

    Returns:
        list: 歌曲信息
    """
    param = {
        "ids": [],
        "mids": mid,
        "types": [0 for i in range(len(mid))],
        "modify_stamp": [0 for i in range(len(mid))],
        "ctx": 0,
        "client": 1,
    }
    res = await Api(**API["query"]).update_params(**param).result
    tracks = res["tracks"]
    return [parse_song_info(song) for song in tracks]


async def get_urls(
    mid: list[str],
    file_type: SongFileType = SongFileType.MP3_128,
    url_type: UrlType = UrlType.PLAY,
    credential: Optional[Credential] = None,
) -> dict[str, str]:
    """
    获取歌曲文件链接
    注：有播放链接，不一定有下载链接

    Args:
        mid:        歌曲 mid
        file_type:  歌曲文件类型. Defaults to SongFileType.MP3_128
        url_type:   歌曲链接类型. Defaults to UrlType.PLAY
        credential: Credential 类. Defaluts to None

    Returns:
        dict: 链接字典
    """
    if credential is None:
        credential = Credential()
    # 分割 id,单次最大请求100
    mid_list = [mid[i : i + 100] for i in range(0, len(mid), 100)]
    # 随机选择文件域名
    domain = (
        "https://isure.stream.qqmusic.qq.com/"
        if url_type == UrlType.PLAY
        else "https://dl.stream.qqmusic.qq.com/"
    )
    api = Api(**API[url_type.value], credential=credential)
    urls = {}
    for mid in mid_list:
        # 构造请求参数
        file_name = [f"{file_type.s}{_}{_}{file_type.e}" for _ in mid]
        param = {
            "filename": file_name,
            "guid": random_string(32, "abcdef1234567890"),
            "songmid": mid,
            "songtype": [1 for _ in range(len(mid))],
        }
        res = await api.update_params(**param).result
        data = res["midurlinfo"]
        for info in data:
            song_url = domain + info["wifiurl"] if info["wifiurl"] else ""
            urls[info["songmid"]] = song_url
    return urls
