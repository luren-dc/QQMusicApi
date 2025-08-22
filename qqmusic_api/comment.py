"""评论 API"""

from typing import Any, cast

from .utils.network import api_request


@api_request("music.globalComment.CommentCountSrv", "GetCmCount")
async def get_comment_count(biz_id: str):
    """获取歌曲评论数量

    Args:
        biz_id: 歌曲 ID
    """
    return {
        "request": {
            "biz_id": biz_id,
            "biz_type": 1,
            "biz_sub_type": 2,
        },
    }, lambda data: cast(dict[str, Any], data.get("response", {}))


def _processor(data: dict[str, Any]):
    """处理并返回结构化评论数据:

    返回结构:
    [
        {
            "Avatar": str,          # 用户头像 URL
            "CmId": str,            # 评论 ID (后续需要获取全部子评论时需用到)
            "PraiseNum": int,       # 点赞数
            "Nick": str,            # 昵称
            "Pic": str,             # 评论配图 (可能为空)
            "Content": str,         # 评论内容
            "SeqNo": str,           # 评论序号 ID 可以用于传递给 参数: last_comment_seq_no
            "SubComments": [        # 子评论列表
                {
                    "Avatar": str,
                    "Nick": str,
                    "Content": str,
                    "Pic": str,
                    "PraiseNum": int,
                    "SeqNo": str
                }
            ]
        },
        ...
    ]
    """
    comments = data.get("CommentList", {}).get("Comments", [])
    result = []

    for comment in comments:
        item = {
            "Avatar": comment.get("Avatar"),
            "CmId": comment.get("CmId"),
            "PraiseNum": comment.get("PraiseNum"),
            "Nick": comment.get("Nick"),
            "Pic": comment.get("Pic"),
            "Content": comment.get("Content"),
            "SeqNo": comment.get("SeqNo"),
            "SubComments": [],
        }

        for sub in comment.get("SubComments", []):
            sub_item = {
                "Avatar": sub.get("Avatar"),
                "Nick": sub.get("Nick"),
                "Content": sub.get("Content"),
                "Pic": sub.get("Pic"),
                "PraiseNum": sub.get("PraiseNum"),
                "SeqNo": sub.get("SeqNo"),
            }
            item["SubComments"].append(sub_item)

        result.append(item)

    return result


@api_request("music.globalComment.CommentRead", "GetHotCommentList")
async def get_hot_comments(
    biz_id: str,
    page_num: int = 1,
    page_size: int = 15,
    last_comment_seq_no: str = "",
):
    """获取歌曲热评

    Args:
        biz_id: 歌曲 ID
        page_num: 页码
        page_size: 每页数量
        last_comment_seq_no: 上一页最后一条评论 ID(可选)
    """
    params = {
        "BizType": 1,
        "BizId": biz_id,
        "LastCommentSeqNo": last_comment_seq_no,
        "PageSize": page_size,
        "PageNum": page_num - 1,
        "HotType": 1,
        "WithAirborne": 0,
        "PicEnable": 1,
    }

    return params, _processor


@api_request("music.globalComment.CommentRead", "GetNewCommentList")
async def get_new_comments(
    biz_id: str,
    page_num: int = 1,
    page_size: int = 15,
    last_comment_seq_no: str = "",
):
    """获取歌曲最新评论

    Args:
        biz_id: 歌曲 ID
        page_num: 页码
        page_size: 每页数量
        last_comment_seq_no: 上一页最后一条评论 ID(可选)
    """
    params = {
        # "LastRspVer": "",
        # "LastTotalVer": "1755832873618224522",
        "PageSize": page_size,
        "PageNum": page_num - 1,
        "HashTagID": "",
        "BizType": 1,
        # "LastCommentId": "",
        "PicEnable": 1,
        "LastCommentSeqNo": last_comment_seq_no,
        "SelfSeeEnable": 1,
        # "LastTotal": 325,
        # "CmListUIVer": 1,
        "BizId": biz_id,
        "AudioEnable": 1,
    }

    return params, _processor


@api_request("music.globalComment.CommentRead", "GetRecCommentList")
async def get_recommend_comments(
    biz_id: str,
    page_num: int = 1,
    page_size: int = 15,
    last_comment_seq_no: str = "",
):
    """获取歌曲推荐评论

    Args:
        biz_id: 歌曲 ID
        page_num: 页码
        page_size: 每页数量
        last_comment_seq_no: 上一页最后一条评论 ID(可选)
    """
    params = {
        # "FromParentCmId": "",
        # "LastRspVer": "1755834843787200911",
        # "LastTotalVer": "1755834843679664122",
        # "RecOffset": 0,
        # "LastHotScore": "",
        # "FromCommentId": "",
        # "HashTagID": "",
        # "CommentIds": [],
        # "LastRecScore": "",
        # "LastTotal": 325,
        "PageSize": page_size,
        "PageNum": page_num - 1,
        "BizType": 1,
        "PicEnable": 1,
        "Flag": 1,
        "LastCommentSeqNo": last_comment_seq_no,
        "CmListUIVer": 1,
        "BizId": biz_id,
        "AudioEnable": 1,
    }

    return params, _processor
