from qqmusic_api.api.song import Song

from ..utils.common import get_api
from ..utils.network import Api

API = get_api("album")


class Album:
    """
    专辑类
    """

    def __init__(self, mid: str):
        """
        Args:
            mid: 专辑 mid
        """
        self.mid = mid

    async def get_detail(self) -> dict:
        """
        Returns:
            dict: 专辑详细信息
        """
        return await Api(**API["detail"]).update_params(albumMid=self.mid).result

    async def get_song(self) -> list[Song]:
        """
        获取专辑歌曲

        Returns:
            list: 歌曲列表
        """
        result = (
            await Api(**API["song"])
            .update_params(albumMid=self.mid, begin=0, num=0)
            .result
        )
        return [Song.from_dict(song["songInfo"]) for song in result["songList"]]
