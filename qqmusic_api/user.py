"""用户相关 API"""

from typing import Optional

from .utils.credential import Credential
from .utils.network import Api
from .utils.utils import get_api

API = get_api("user")


async def get_created_songlist(musicid: int) -> list[dict]:
    """通过 musicid 获取用户创建的歌单

    Args:
        musicid: QQ音乐 musicid

    Returns:
        歌单列表
    """
    result = await Api(**API["songlist_by_uin"]).update_params(uin=str(musicid)).result
    return result["v_playlist"]


async def get_login_user_info(credential: Credential) -> dict:
    """获取登录用户信息

    Args:
        credential: 用户凭证

    Returns:
        用户信息
    """
    return (await Api(**API["login_user_info"], credential=credential).result)["info"]


class User:
    """用户类

    Attributes:
        euin:       QQ音乐 encrypt_uin
        credential: 账号凭证
    """

    def __init__(self, euin: Optional[str], credential: Credential):
        """初始化用户类

        Note:
            euin 为 None 时，使用 credential 中的 euin

        Args:
            euin:       QQ音乐 encrypt_uin
            credential: 账号凭证
        """
        if euin is None:
            self.euin = credential.encrypt_uin
        else:
            self.euin = euin
        self.credential = credential

    async def get_fav_songlist(self):
        """获取收藏歌单

        Returns:
            收藏歌单列表
        """
        return await Api(**API["fav_songlist_by_euin"], credential=self.credential).update_params(uin=self.euin).result
