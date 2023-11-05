from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Dict, List

from ..utils import parse_song_info

if TYPE_CHECKING:
    from qqmusic import QQMusic


class AlbumApi:
    """专辑Api"""

    parent: ClassVar[QQMusic]

    @staticmethod
    async def detail(mid: str) -> Dict:
        """
        获取专辑信息

        Args:
            mid: 专辑mid

        Returns:
            专辑信息
        """
        response = await AlbumApi.parent.get_data(
            module="music.musichallAlbum.AlbumInfoServer",
            method="GetAlbumDetail",
            param={"albumMid": mid},
        )
        response["info"] = response.pop("basicInfo", {})
        response["singer"] = response.pop("singer", {}).get("singerList", [])
        return response

    @staticmethod
    async def song(mid: str) -> List[Dict]:
        """
        获取专辑歌曲

        Args:
            mid: 专辑mid

        Returns:
            歌曲信息
        """
        response = await AlbumApi.parent.get_data(
            module="music.musichallAlbum.AlbumSongList",
            method="GetAlbumSongList",
            param={"albumMid": mid, "order": 2, "begin": 0, "num": -1},
        )
        return [parse_song_info(song["songInfo"]) for song in response["songList"]]
