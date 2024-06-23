from typing import Optional

from qqmusic_api.api.song import Song

from ..utils.common import get_api
from ..utils.network import Api

API = get_api("songlist")


class Songlist:
    """
    歌单类
    """

    def __init__(self, id: int):
        """
        Args:
            id: 歌单 ID
        """
        self.id = id
        self._info: Optional[dict] = None

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
            result = (
                await Api(**API["detail"])
                .update_params(**param)
                .update_headers(Referer="")
                .result
            )
            self._info = result  # type: ignore
        return self._info

    async def get_detail(self) -> dict:
        """
        获取歌单详细信息

        Returns:
            dict: 歌单信息
        """
        result = await self.__get_info()
        return result["dirinfo"]

    async def get_song(self) -> list[Song]:
        """
        获取歌单歌曲

        Returns:
            list: 歌单歌曲
        """
        result = await self.__get_info()
        return [Song.from_dict(song) for song in result["songlist"]]

    async def get_song_tag(self) -> list[dict]:
        """
        获取歌单歌曲标签
        注：存在几率返回为空

        Returns:
            list: 歌单歌曲标签
        """
        result = await self.__get_info()
        return result["songtag"]

    async def get_song_mid(self) -> list[dict]:
        """
        获取歌单歌曲全部 mid

        Returns:
            list: 歌单歌曲 mid
        """
        result = await self.__get_info()
        return [song["mid"] for song in result["songlist"]]
