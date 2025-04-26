"""评论 API"""

import json
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

        # 输出为 JSON 格式字符串
        json_output = json.dumps(result, ensure_ascii=False, indent=2)
        print(json_output)
        return result

    return params, _processor
