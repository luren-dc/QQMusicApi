"""排行榜相关 API"""

from .utils.common import get_api
from .utils.network import Api

API = get_api("top")


async def get_top_category() -> list[dict]:
    """获取所有排行榜

    Returns:
        排行榜信息
    """
    return (await Api(**API["category"]).result)["group"]


# TODO: 支持设置日期
class Top:
    """排行榜类

    Attributes:
        id: 排行榜 ID
    """

    def __init__(
        self,
        id: int,
    ) -> None:
        """初始化排行榜类

        Args:
            id: 排行榜 ID
        """
        self.id = id

    async def get_detail(self) -> dict:
        """获取排行榜详细信息

        Returns:
            排行榜信息
        """
        return (await Api(**API["detail"]).update_params(topId=self.id, num=100).result)["data"]

    async def get_song(self) -> list[dict]:
        """获取排行榜歌曲信息

        Returns:
            排行榜歌曲信息
        """
        param = {"topId": self.id, "offset": 0, "num": 100}
        return (await Api(**API["detail"]).update_params(**param).result)["songInfoList"]
