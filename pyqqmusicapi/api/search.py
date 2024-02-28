from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List

if TYPE_CHECKING:
    from ..qqmusic import QQMusic

from ..utils import filter_data, parse_song_info, random_searchID


class SearchApi:
    """搜索Api"""

    parent: ClassVar[QQMusic]

    @staticmethod
    async def integrate(keyword: str, highlight: bool = False) -> Dict[str, Any]:
        """
        综合搜索

        Args:
            keyword: 关键词
            highlight: 高亮

        Returns:
            包含直接结果，歌曲，歌手，专辑，歌单，mv等
        """
        response = await SearchApi.parent.get_data(
            module="music.adaptor.SearchAdaptor",
            method="do_search_v2",
            param={
                "search_id": random_searchID(),
                "search_type": 100,
                "query": keyword,
                "highlight": 1 if highlight else 0,
                "nqc_flag": 0,
                "grp": 1,
                "multi_zhida": 1,
            },
        )
        data = response["body"]
        direct = [filter_data(d) for d in data["direct_result"]["vertical_list"]]
        song = [parse_song_info(d) for d in data["item_song"]["items"]]
        album = [filter_data(d) for d in data["item_album"]["items"]]
        songlist = [filter_data(d) for d in data["item_songlist"]["items"]]
        mv = [filter_data(d) for d in data["item_mv"]["items"]]
        audio = [filter_data(d) for d in data["item_audio"]["items"]]
        audio_song = [filter_data(d) for d in data["item_audiosong"]["items"]]
        user = [filter_data(d) for d in data["item_user"]["items"]]
        singer = [filter_data(d) for d in data["singer"]["items"]]
        return {
            "direct": direct,
            "song": song,
            "singer": singer,
            "album": album,
            "songlist": songlist,
            "mv": mv,
            "user": user,
            "audio": audio,
            "audioSong": audio_song,
        }

    @staticmethod
    async def quick(keyword: str) -> Dict[str, Any]:
        """
        快速搜索

        Args:
            keyword: 关键词

        Returns:
            包含专辑，歌手，歌曲的简略信息
        """
        response = await SearchApi.parent.get(
            f"https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg?key={keyword}"
        )
        return json.loads(await response.text())["data"]

    @staticmethod
    async def hotkey() -> List[Dict]:
        """
        获取热搜词

        Returns:
            热搜词列表，k为热搜词，n为搜索量
        """
        response = await SearchApi.parent.get_data(
            module="music.musicsearch.HotkeyService",
            method="GetHotkeyForQQMusicMobile",
            param={"search_id": random_searchID()},
        )
        data = response.get("vec_hotkey", [])
        return [{"k": hotkey["query"], "n": hotkey["score"]} for hotkey in data]

    @staticmethod
    async def completion(keyword: str, highlight: bool = False) -> List[str]:
        """
        搜索词补全

        Args:
            keyword: 查询词
            highlight: 高亮

        Returns:
            补全结果列表
        """
        response = await SearchApi.parent.get_data(
            module="tencent_music_soso_smartbox_cgi.SmartBoxCgi",
            method="GetSmartBoxResult",
            param={
                "search_id": random_searchID(),
                "query": keyword,
                "num_per_page": 10,
                "highlight": 1 if highlight else 0,
                "page_idx": 1,
            },
        )
        data = response["items"]
        if highlight:
            return [item["hint_hilight"] for item in data]
        else:
            return [item["hint"] for item in data]

    @staticmethod
    async def query(
        keyword: str,
        query_type: int = 0,
        num: int = 10,
        page: int = 1,
        highlight: bool = False,
        selectors: Dict[str, str] = {},
    ) -> List[Dict[str, Any]]:
        """
        搜索

        Args:
            keyword: 关键词
            query_type:
                搜索类型
                song：0 不支持返回数量
                singer：1
                album：2
                songlist：3
                mv：4
                lyric：7
                user：8
                audio：15
                audio_song：18
            num: 返回数量
            page: 返回页数
            selectors: 选择器
            highlight: 高亮

        Returns:
            搜索结果

        Raises:
            ValueError: 搜索类型错误
        """
        # 确保搜索类型正确
        if query_type not in [0, 1, 2, 3, 4, 7, 8, 15, 18, 22]:
            raise ValueError("搜索类型错误")

        types = {
            0: "item_song",
            1: "singer",
            2: "item_album",
            3: "item_songlist",
            4: "item_mv",
            7: "item_song",
            8: "item_user",
            15: "item_audio",
            18: "item_song",
        }

        response = await SearchApi.parent.get_data(
            module="music.search.SearchCgiService",
            method="DoSearchForQQMusicMobile",
            param={
                "search_id": random_searchID(),
                "query": keyword,
                "search_type": query_type,
                "num_per_page": num,
                "page_num": page,
                "highlight": 1 if highlight else 0,
                "nqc_flag": 0,
                "page_id": page,
                "grp": 1,
                "selectors": selectors,
            },
        )
        data = response["body"].get(types[query_type], [])
        if query_type in [0, 7, 18]:
            return [parse_song_info(song) for song in data]
        return [filter_data(d) for d in data]

    @staticmethod
    async def selectors(
        keyword: str,
        query_type: int = 0,
    ) -> Dict[str, Any]:
        """
        获取搜索选择器

        Args:
            keyword: 关键词
            query_type:
                搜索类型
                song：0
                singer：1
                album：2
                songlist：3
                mv：4
                lyric：7
                user：8
                audio：15
                audio_song：18

        Returns:
            搜索选择器

        Raises:
            ValueError: 搜索类型错误
        """
        # 确保搜索类型正确
        if query_type not in [0, 1, 2, 3, 4, 7, 8, 15, 18, 22]:
            raise ValueError("搜索类型错误")

        response = await SearchApi.parent.get_data(
            module="music.search.SearchCgiService",
            method="DoSearchForQQMusicMobile",
            param={
                "search_id": random_searchID(),
                "query": keyword,
                "search_type": query_type,
            },
        )
        data = response["body"]
        return data["multi_extern_info"]["selectors"]

    @staticmethod
    async def singer_list(
            letter: str = 'a',
            sex: int = -100,
            area: int = 200,
            genre: int = -100,
        ) -> List[Dict]:
        """
        搜索歌手列表

        Args:
            letter: 首字母 (a..z#), 默认为 a, 如果要查询所有歌手请设为 None
            area: 地区: 内地 200, 港台 2, 韩国 3, 日本 4, 欧美 5
            sex: 性别: 男 0, 女 1, 组合 2
            genre: 类型
                流行: 7
                说唱: 3
                国风: 19
                摇滚: 4
                电子: 2
                民谣: 8
                R&B: 11
                民族乐: 37
                轻音乐: 93
                爵士: 14
                古典: 33
                乡村: 13
                蓝调: 10

        Returns:
            歌手列表

        Raises:
            ValueError: letter 输入错误
        """
        index = -100
        if letter is not None:
            if len(letter) != 1:
                raise ValueError("letter must be a single character")
            letter = letter.upper()
            if letter not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#':
                raise ValueError("letter must be a-z or #")
            if letter == '#':
                index = 27
            else:
                index = ord(letter) - ord('A') + 1

        response = await SearchApi.parent.get_data(
            module="music.musichallSinger.SingerList",
            method="GetSingerListIndex",
            param={
                "area": area,
                "sex": sex,
                "genre": genre,
                "index": index,
                "sin": 0,
                "cur_page": 1,
            },
        )

        singer_list = response["singerlist"]
        total = response["total"]
        if total <= 80:
            return singer_list

        # 每页80个歌手，向下取整
        pages = total // 80
        sin = 80
        for page in range(2, pages + 2):
            response = await SearchApi.parent.get_data(
                module="music.musichallSinger.SingerList",
                method="GetSingerListIndex",
                param={
                    "area": area,
                    "sex": sex,
                    "genre": genre,
                    "index": index,
                    "sin": sin,
                    "cur_page": page,
                },
            )
            singer_list.extend(response["singerlist"])
            sin += 80

        return singer_list
