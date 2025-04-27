"""评论 API"""

from typing import Any

from qqmusic_api.utils.network import api_request


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
        "PageNum": page_num,
        "HotType": 1,
        "WithAirborne": 0,
        "PicEnable": 1,
    }

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

    return params, _processor
