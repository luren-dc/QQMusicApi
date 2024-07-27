"""歌单相关 API"""

from typing import Optional

from .song import Song
from .utils.network import Api
from .utils.utils import get_api

API = get_api("songlist")


class Songlist:
    """歌单类

    Attributes:
        id: 歌单 ID
    """

    def __init__(self, id: int):
        """初始化歌单类

        Args:
            id: 歌单 ID
        """
        self.id = id
        self._info: Optional[dict] = None

    def __repr__(self) -> str:
        return f"Songlist(id={self.id})"

    def __str__(self) -> str:
        if self._info:
            return str(self._info)
        return self.__repr__()

    async def __get_info(self):
        if not self._info:
            param = {
                "disstid": self.id,
                "dirid": 0,
                "tag": True,
                "song_num": 0,
                "userinfo": True,
                "orderlist": True,
            }
            result = await Api(**API["detail"]).update_params(**param).update_headers(Referer="").result
            self._info = result  # type: ignore
        return self._info

    async def get_detail(self) -> dict:
        """获取歌单详细信息

        Returns:
            歌单信息
        """
        result = await self.__get_info()
        return result["dirinfo"]

    async def get_song(self) -> list[Song]:
        """获取歌单歌曲

        Returns:
            歌单歌曲
        """
        result = await self.__get_info()
        return [Song.from_dict(song) for song in result["songlist"]]

    async def get_song_tag(self) -> list[dict]:
        """获取歌单歌曲标签
        注：存在几率返回为空

        Returns:
            歌单歌曲标签
        """
        result = await self.__get_info()
        return result["songtag"]

    async def get_song_mid(self) -> list[str]:
        """获取歌单歌曲全部 mid

        Returns:
            歌单歌曲 mid
        """
        result = await self.__get_info()
        return [song["mid"] for song in result["songlist"]]
