"""歌单相关 API"""

from typing import Any, cast

from .utils.network import RequestGroup, api_request


@api_request("music.srfDissInfo.DissInfo", "CgiGetDiss")
async def get_detail(
    songlist_id: int,
    dirid: int = 0,
    num: int = 10,
    page: int = 1,
    onlysong: bool = False,
    tag: bool = True,
    userinfo: bool = True,
):
    """获取歌单详细信息和歌曲

    Args:
        songlist_id: 歌单 ID
        dirid: 歌单 dirid
        num: 返回数量
        page: 页码
        onlysong: 是否仅返回歌曲信息(优先级最大)
        tag: 是否返回歌单的标签信息
        userinfo: 是否返回歌单创建者的用户信息
    """

    def _processsor(data: dict[str, Any]):
        return {
            "dirinfo": data.get("dirinfo", {}),
            "total_song_num": data.get("total_song_num", 0),
            "songlist_size": data.get("songlist_size", 0),
            "songlist": data.get("songlist", []),
            "songtag": data.get("songtag", []),
            "orderlist": data.get("orderlist", []),
        }

    return {
        "disstid": songlist_id,
        "dirid": dirid,
        "tag": tag,
        "song_begin": num * (page - 1),
        "song_num": num,
        "userinfo": userinfo,
        "orderlist": True,
        "onlysonglist": onlysong,
    }, _processsor


async def get_songlist(
    songlist_id: int,
    dirid: int = 0,
):
    """获取歌单中所有歌曲列表

    Args:
        songlist_id: 歌单 ID
        dirid: 歌单 dirid
    """
    response = await get_detail(songlist_id=songlist_id, dirid=dirid, onlysong=True)

    total = response["total_song_num"]
    songs = response["songlist"]
    if total <= 100:
        return cast(list[dict[str, Any]], songs)

    rg = RequestGroup()
    for p, num in enumerate(range(100, total, 100), start=2):
        rg.add_request(get_detail, songlist_id=songlist_id, dirid=dirid, num=100, page=p, onlysong=True)

    response = await rg.execute()
    for res in response:
        songs.extend(res["songlist"])

    return cast(list[dict[str, Any]], songs)
