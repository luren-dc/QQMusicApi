"""专辑相关 API"""

from typing import Any, Literal

from .utils.network import NO_PROCESSOR, api_request


def get_cover(mid: str, size: Literal[150, 300, 500, 800] = 300) -> str:
    """获取专辑封面链接

    Args:
        mid: 专辑 mid
        size: 封面大小

    Returns:
        封面链接
    """
    if size not in [150, 300, 500, 800]:
        raise ValueError("not supported size")
    return f"https://y.gtimg.cn/music/photo_new/T002R{size}x{size}M000{mid}.jpg"


@api_request("music.musichallAlbum.AlbumInfoServer", "GetAlbumDetail")
async def get_detail(value: str | int):
    """获取专辑详细信息

    Args:
        value: 专辑 id 或 mid
    """
    if isinstance(value, int):
        return {"albumId": value}, NO_PROCESSOR

    return {"albumMId": value}, NO_PROCESSOR


@api_request("music.musichallAlbum.AlbumSongList", "GetAlbumSongList")
async def get_song(value: str | int, num: int = 10, page: int = 1):
    """获取专辑歌曲

    Args:
        value: 专辑 id 或 mid
        num: 返回数量
        page: 页码
    """
    params: dict[str, Any] = {
        "begin": num * (page - 1),
        "num": num,
    }

    def _processor(data: dict[str, Any]) -> list[dict[str, Any]]:
        return [song["songInfo"] for song in data["songList"]]

    if isinstance(value, int):
        params["albumId"] = value
    else:
        params["albumMid"] = value

    return params, _processor
