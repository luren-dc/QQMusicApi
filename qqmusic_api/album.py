"""专辑相关 API"""

from typing import Optional

from .song import Song
from .utils.network import Api
from .utils.utils import get_api

API = get_api("album")


class Album:
    """专辑类

    Attributes:
        mid: 专辑 mid
    """

    def __init__(
        self,
        mid: Optional[str] = None,
        id: Optional[int] = None,
    ):
        """初始化专辑类

        Args:
            mid: 专辑 mid
            id: 专辑 id
        """
        # ID 检查
        if mid is None and id is None:
            raise ValueError("mid or id must be provided")
        self.mid = mid
        self.id = id

    def __repr__(self) -> str:
        return f"Album(mid={self.mid}, id={self.id})"

    async def get_detail(self) -> dict:
        """获取专辑详细信息

        Returns:
            专辑详细信息
        """
        return await Api(**API["detail"]).update_params(albumMid=self.mid, albumId=self.id).result

    async def get_song(self) -> list[Song]:
        """获取专辑歌曲

        Returns:
            歌曲列表
        """
        result = await Api(**API["song"]).update_params(albumMid=self.mid, albumId=self.id, begin=0, num=0).result
        return [Song.from_dict(song["songInfo"]) for song in result["songList"]]
