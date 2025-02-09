"""排行榜相关 API"""

from typing import Any, cast

from .utils.network import NO_PROCESSOR, api_request


@api_request("music.musicToplist.Toplist", "GetAll")
async def get_top_category():
    """获取所有排行榜"""
    return {}, lambda data: cast(list[dict[str, Any]], data.get("group", []))


@api_request("music.musicToplist.Toplist", "GetDetail", process_bool=False)
async def get_detail(
    top_id: int,
    num: int = 10,
    page: int = 1,
    tag: bool = True,
):
    """获取排行榜详细信息

    Args:
        top_id: 排行榜 id
        num: 返回数量
        page: 页码
        tag: 是否返回歌曲标签
    """
    return {
        "topId": top_id,
        "offset": num * (page - 1),
        "num": num,
        "withTags": tag,
    }, NO_PROCESSOR
