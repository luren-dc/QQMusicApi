"""歌手相关 API"""

from enum import Enum
from typing import Literal, Optional

from .utils.common import get_api
from .utils.network import Api

API = get_api("singer")


class AreaType(Enum):
    """地区

    + ALL:     全部
    + CHINA:   内地
    + TAIWAN:  台湾
    + AMERICA: 美国
    + EUROPE:  欧美
    + JAPAN:   日本
    + KOREA:   韩国
    """

    ALL = -100
    CHINA = 200
    TAIWAN = 2
    AMERICA = 5
    EUROPE = 4
    JAPAN = 3
    KOREA = 1


class GenreType(Enum):
    """风格

    + ALL:           全部
    + POP:           流行
    + RAP:           说唱
    + CHINESE_STYLE: 国风
    + ROCK:          摇滚
    + ELECTRONIC:    电子
    + FOLK:          民谣
    + R_AND_B:       R&B
    + ETHNIC:        民族乐
    + LIGHT_MUSIC:   轻音乐
    + JAZZ:          爵士
    + CLASSICAL:     古典
    + COUNTRY:       乡村
    + BLUES:         蓝调
    """

    ALL = -100
    POP = 7
    RAP = 3
    CHINESE_STYLE = 19
    ROCK = 4
    ELECTRONIC = 2
    FOLK = 8
    R_AND_B = 11
    ETHNIC = 37
    LIGHT_MUSIC = 93
    JAZZ = 14
    CLASSICAL = 33
    COUNTRY = 13
    BLUES = 10


class SexType(Enum):
    """性别

    + ALL:    全部
    + MALE:   男
    + FEMALE: 女
    + GROUP:  组合
    """

    ALL = -100
    MALE = 0
    FEMALE = 1
    GROUP = 2


class TabType(Enum):
    """Tab 类型

    + WIKI:     wiki
    + ALBUM:    专辑
    + COMPOSER: 作曲
    + LYRICIST: 作词
    + PRODUCER: 制作人
    + ARRANGER: 编曲
    + MUSICIAN: 乐手
    + SONG:     歌曲
    + VIDEO:    视频
    """

    WIKI = ("wiki", "IntroductionTab")
    ALBUM = ("album", "AlbumTab")
    COMPOSER = ("song_composing", "SongTab")
    LYRICIST = ("song_lyric", "SongTab")
    PRODUCER = ("producer", "SongTab")
    ARRANGER = ("arranger", "SongTab")
    MUSICIAN = ("musician", "SongTab")
    SONG = ("song_sing", "SongTab")
    VIDEO = ("video", "VideoTab")

    def __init__(self, tab_id: str, tab_name: str) -> None:
        self.tab_id = tab_id
        self.tab_name = tab_name


async def get_singer_list(
    area: AreaType = AreaType.ALL,
    sex: SexType = SexType.ALL,
    genre: GenreType = GenreType.ALL,
) -> list:
    """获取歌手列表

    Args:
        area:  地区.Defaluts to AreaType.ALL
        sex:   性别.Defaluts to SexType.ALL
        genre: 风格.Defaluts to GenreType.ALL

    Returns:
        歌手列表
    """
    result = (
        await Api(**API["singer_list"])
        .update_params(
            hastag=0,
            area=area.value,
            sex=sex.value,
            genre=genre.value,
        )
        .result
    )
    return result["hotlist"]


class Singer:
    """歌手类

    Args:
        mid: 歌手 mid
    """

    def __init__(self, mid: str) -> None:
        """初始化歌手类

        Args:
            mid: 歌手 mid
        """
        self.mid = mid
        self._info: Optional[dict] = None

    async def get_info(self) -> dict:
        """获取歌手信息

        Returns:
            歌手信息
        """
        if not self._info:
            self._info = await Api(**API["homepage"]).update_params(SingerMid=self.mid).result
        return self._info

    async def get_tab_detail(self, tab_type: TabType, page: int = 1, num: int = 100) -> dict:
        """获取歌手主页 Tab 详细信息

        Args:
            tab_type: Tab 类型
            page:     页码
            num:      返回数量

        Returns:
            Tab 详细信息
        """
        return (
            await Api(**API["homepage_tab_detail"])
            .update_params(
                SingerMid=self.mid,
                IsQueryTabDetail=1,
                TabID=tab_type.tab_id,
                PageNum=page - 1,
                PageSize=num,
                Order=0,
            )
            .result
        )[tab_type.tab_name]

    async def get_wiki(self) -> dict:
        """获取歌手WiKi

        Returns:
            歌手WiKi
        """
        return await self.get_tab_detail(TabType.WIKI)

    async def get_song(
        self,
        type: Literal[
            TabType.SONG,
            TabType.ALBUM,
            TabType.COMPOSER,
            TabType.LYRICIST,
            TabType.PRODUCER,
            TabType.ARRANGER,
            TabType.MUSICIAN,
        ] = TabType.SONG,
        page: int = 1,
        num: int = 100,
    ) -> list[dict]:
        """获取歌手歌曲

        Args:
            type: Tab 类型
            page: 页码
            num:  返回数量

        Returns:
            歌曲信息列表
        """
        data = await self.get_tab_detail(type, page, num)
        return data["List"]
