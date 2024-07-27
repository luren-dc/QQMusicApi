"""专辑相关 API"""

from .song import Song
from .utils.network import Api
from .utils.utils import get_api

API = get_api("album")


class Album:
    """专辑类

    Attributes:
        mid: 专辑 mid
    """

    def __init__(self, mid: str):
        """初始化专辑类

        Args:
            mid: 专辑 mid
        """
        self.mid = mid

    def __repr__(self) -> str:
        return f"Album(mid={self.mid})"

    async def get_detail(self) -> dict:
        """获取专辑详细信息

        Returns:
            专辑详细信息
        """
        return await Api(**API["detail"]).update_params(albumMid=self.mid).result

    async def get_song(self) -> list[Song]:
        """获取专辑歌曲

        Returns:
            歌曲列表
        """
        result = await Api(**API["song"]).update_params(albumMid=self.mid, begin=0, num=0).result
        return [Song.from_dict(song["songInfo"]) for song in result["songList"]]
