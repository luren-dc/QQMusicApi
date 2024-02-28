from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Dict, List

if TYPE_CHECKING:
    from qqmusic import QQMusic

from ..utils import parse_song_info

import asyncio

class SingerApi:
    """歌手API"""

    parent: ClassVar[QQMusic]

    @staticmethod
    async def detail(mid: str) -> Dict[str, Any]:
        """
        歌手详细信息

        Args:
            mid: 歌手mid

        Returns:
            Dict: 歌手信息
        """
        response = await SingerApi.parent.get_data(
            module="music.musichallSinger.SingerInfoInter",
            method="GetSingerDetail",
            param={"singer_mids": [mid]},
        )

        return response["singer_list"][0]

    @staticmethod
    async def song(mid: str) -> List[Dict]:
        """
        歌手歌曲

        Args:
            mid: 歌手mid

        Returns:
            List: 歌曲列表
        """
        # 每次最多允许获取30首歌曲
        response = await SingerApi.parent.get_data(
            module="musichall.song_list_server",
            method="GetSingerSongList",
            param={"singerMid": mid,
                   "order": 1,
                   "number": 30,
                   "begin": 0,
                   },
        )

        total = response["totalNum"]
        songs = [parse_song_info(song["songInfo"]) for song in response["songList"]]
        if total <= 30:
            return songs

        tasks = []
        for num in range(30, total, 30):
            tasks.append(SingerApi.parent.get_data(
                module="musichall.song_list_server",
                method="GetSingerSongList",
                param={"singerMid": mid,
                       "order": 1,
                       "number": 30,
                       "begin": num,
                       },
            ))
        response = await asyncio.gather(*tasks)
        for res in response:
            songs.extend([parse_song_info(song["songInfo"]) for song in res["songList"]])

        return songs

    @staticmethod
    async def album(mid: str) -> List[Dict]:
        """
        歌手专辑

        Args:
            mid: 歌手mid

        Returns:
            List: 专辑列表
        """
        response = await SingerApi.parent.get_data(
            module="music.musichallAlbum.AlbumListServer",
            method="GetAlbumList",
            param={"singerMid": mid,
                   "order": 1,
                   "number": 30,
                   "begin": 0,
                   },
        )

        total = response["total"]
        albums = response["albumList"]
        if total <= 30:
            return albums

        tasks = []
        for num in range(30, total, 30):
            tasks.append(SingerApi.parent.get_data(
                module="music.musichallAlbum.AlbumListServer",
                method="GetAlbumList",
                param={"singerMid": mid,
                       "order": 1,
                       "number": 30,
                       "begin": num,
                       },
            ))
        response = await asyncio.gather(*tasks)
        for res in response:
            albums.extend(res["albumList"])

        return albums

    @staticmethod
    async def mv(mid: str) -> List[Dict]:
        """
        歌手MV

        Args:
            mid: 歌手mid

        Returns:
            List: mv列表
        """
        response = await SingerApi.parent.get_data(
            module="MvService.MvInfoProServer",
            method="GetSingerMvList",
            param={"singermid": mid,
                   "order": 1,
                   "count": 100,
                   "start": 0,
                   },
        )

        total = response["total"]
        mv = response["list"]
        if total <= 100:
            return mv

        tasks = []
        for num in range(100, total, 100):
            tasks.append(SingerApi.parent.get_data(
                module="MvService.MvInfoProServer",
                method="GetSingerMvList",
                param={"singermid": mid,
                       "order": 1,
                       "count": 100,
                       "start": num,
                       },
            ))
        response = await asyncio.gather(*tasks)
        for res in response:
            mv.extend(res["list"])

        return mv

    @staticmethod
    async def similar(mid: str, number: int = 10) -> List[Dict]:
        """
        类似歌手

        Args:
            mid: 歌手mid
            number: 返回类似歌手数量

        Returns:
            List: 类似歌手
        """
        response = await SingerApi.parent.get_data(
            module="music.SimilarSingerSvr",
            method="GetSimilarSingerList",
            param={"singerMid": mid,
                   "number": number,
                   },
        )

        return response["singerlist"]
