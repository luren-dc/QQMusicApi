"""歌单相关 API"""

from .utils.common import get_api
from .utils.network import Api

API = get_api("songlist")


class Songlist:
    """歌单类

    Attributes:
        id: 歌单 ID
    """

    def __init__(self, id: int, dirid: int = 0):
        """初始化歌单类

        Args:
            id: 歌单 ID
            dirid: 歌单 dirid
        """
        self.id = id
        self.dirid = dirid

    async def get_detail(self) -> dict:
        """获取歌单详细信息

        Returns:
            歌单信息
        """
        param = {
            "disstid": self.id,
            "dirid": self.dirid,
            "tag": False,
            "song_num": 1,
            "userinfo": True,
            "orderlist": True,
        }
        return (await Api(**API["detail"]).update_params(**param).result)["dirinfo"]

    async def get_song(self) -> list[dict]:
        """获取歌单歌曲

        Returns:
            歌单歌曲
        """
        param = {"disstid": self.id, "onlysonglist": True}
        return (await Api(**API["detail"]).update_params(**param).result)["songlist"]

    async def get_song_tag(self) -> list[dict]:
        """获取歌单歌曲标签

        Returns:
            歌曲标签
        """
        param = {"disstid": self.id, "song_num": 1, "tag": True}
        return (await Api(**API["detail"]).update_params(**param).result)["songtag"]
