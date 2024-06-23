from enum import Enum

from ..utils.common import get_api
from ..utils.network import Api

API = get_api("singer")


class AreaType(Enum):
    """
    地区

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
    """
    风格

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
    """
    性别

    + ALL:    全部
    + MALE:   男
    + FEMALE: 女
    + GROUP:  组合
    """

    ALL = -100
    MALE = 0
    FEMALE = 1
    GROUP = 2


async def get_singer_list(
    area: AreaType = AreaType.ALL,
    sex: SexType = SexType.ALL,
    genre: GenreType = GenreType.ALL,
) -> list:
    """
    获取歌手列表

    Args:
        area:  地区.Defaluts to AreaType.ALL
        sex:   性别.Defaluts to SexType.ALL
        genre: 风格.Defaluts to GenreType.ALL

    Returns:
        list: 歌手列表
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
    """
    歌手类
    """

    def __init__(self, mid: str) -> None:
        """
        Args:
            mid: 歌手 mid
        """
        self.mid = mid
