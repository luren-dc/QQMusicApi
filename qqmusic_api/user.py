"""用户相关 API"""

from typing import Optional

from .exceptions import ResponseCodeError
from .utils.common import get_api
from .utils.credential import Credential
from .utils.network import Api

API = get_api("user")


async def get_created_songlist(musicid: int) -> list[dict]:
    """通过 musicid 获取用户创建的歌单

    Args:
        musicid: musicid

    Returns:
        歌单列表
    """
    result = await Api(**API["songlist_by_uin"]).update_params(uin=str(musicid)).result
    return result["v_playlist"]


async def get_euin(musicid: int) -> str:
    """通过 musicid 获取 euin

    Args:
        musicid: 需要获取 euin 的 musicid

    Returns:
        获取到的 encrypt_uin,为空表示获取失败
    """
    try:
        result = await Api(**API["profile"]).update_params(ct=20, cv=4747474, cid=205360838, userid=musicid).result
    except ResponseCodeError:
        return ""
    return result["creator"]["encrypt_uin"]


async def get_musicid(euin: str) -> int:
    """通过 euin 获取 musicid


    Args:
        euin: 需要获取 musicid 的 euin

    Returns:
        获取到的 musicid,0 表示获取失败
    """
    api = get_api("songlist")["detail"]
    try:
        result = (
            await Api(**api)
            .update_params(
                disstid=0,
                dirid=201,
                song_num=1,
                enc_host_uin=euin,
            )
            .result
        )
    except ResponseCodeError:
        return 0
    if result["code"] != 0:
        return 0
    return int(result["dirinfo"]["creator"]["musicid"])


async def get_vip_info(credential: Credential) -> dict:
    """获取 VIP 信息

    Args:
        credential: 账号凭据

    Returns:
        VIP 相关信息
    """
    return await Api(**API["vip_info"], credential=credential).result


class User:
    """用户类

    Attributes:
        euin:       encrypt_uin
        credential: 账号凭证
    """

    def __init__(self, euin: str, credential: Optional[Credential] = None):
        """初始化用户类

        传入有效 credential 获取他人的信息会更完整但会留痕,且部分 API 不会验证
        credential 是否有效,强制 credential 的 API 在 credential 失效时会报错

        Args:
            euin:       encrypt_uin
            credential: 账号凭证
        """
        self.euin = euin
        self.credential = credential or Credential(musicid=1, musickey="None")

    async def get_homepage(self) -> dict:
        """获取主页信息

        Returns:
            主页信息
        """
        return (
            await Api(**API["homepage"], credential=self.credential)
            .update_params(IsQueryTabDetail=1, uin=self.euin)
            .result
        )

    async def get_created_songlist(self) -> list[dict]:
        """获取创建的歌单

        Returns:
            歌单列表
        """
        result = (
            await Api(**API["songlist_by_euin"], credential=self.credential)
            .update_params(hostuin=self.euin, sin=0, size=1000)
            .result
        )
        data = result["disslist"]
        data.pop(0)
        return data

    async def get_fav_song(self, num: int = 10, page: int = 1) -> dict:
        """获取收藏歌单

        Args:
            num:  数量
            page: 页码

        Returns:
            收藏歌单列表
        """
        api = get_api("songlist")["detail"]
        result = (
            await Api(**api, credential=self.credential)
            .update_params(
                disstid=0,
                dirid=201,
                song_num=num,
                song_begin=(page - 1) * num,
                enc_host_uin=self.euin,
                onlysonglist=1,
            )
            .result
        )
        total = result["total_song_num"]

        return {"total": total, "hasmore": int(total > page * num), "list": result["songlist"]}

    async def get_fav_songlist(self, num: int = 10, page: int = 1) -> dict:
        """获取收藏歌单

        Args:
            num:  数量
            page: 页码

        Returns:
            收藏歌单列表
        """
        return (
            await Api(**API["fav_songlist_by_euin"], credential=self.credential)
            .update_params(uin=self.euin, offset=num * (page - 1), size=num)
            .result
        )

    async def get_fav_album(self, num: int = 10, page: int = 1) -> dict:
        """获取收藏专辑

        Args:
            num:  数量
            page: 页码

        Returns:
            收藏专辑列表
        """
        return (
            await Api(**API["fav_album_by_euin"], credential=self.credential)
            .update_params(euin=self.euin, offset=num * (page - 1), size=num)
            .result
        )

    async def get_fav_mv(self, num: int = 10, page: int = 1) -> dict:
        """获取收藏 MV

        Args:
            num:  数量
            page: 页码

        Returns:
            收藏 MV 列表
        """
        result = (
            await Api(**API["fav_mv_by_euin"], credential=self.credential)
            .update_params(encuin=self.euin, pagesize=num, num=page - 1)
            .result
        )
        return {"hasmore": result["hasmore"], "total": result["total"], "list": result["mvlist"]}

    async def get_follow_user(self, num: int = 10, page: int = 1) -> dict:
        """获取关注用户

        Args:
            num:  数量
            page: 页码

        Returns:
            关注用户信息
        """
        result = (
            await Api(**API["follow_user"], credential=self.credential)
            .update_params(HostUin=self.euin, From=num * (page - 1), Size=num)
            .result
        )
        return {"total": result["Total"], "list": result["List"]}

    async def get_follow_singer(self, num: int = 10, page: int = 1) -> dict:
        """获取关注歌手

        Args:
            num:  数量
            page: 页码

        Returns:
            关注歌手信息
        """
        result = (
            await Api(**API["follow_singer"], credential=self.credential)
            .update_params(HostUin=self.euin, From=num * (page - 1), Size=num)
            .result
        )
        return {"total": result["Total"], "list": result["List"]}

    async def get_fans(self, num: int = 10, page: int = 1) -> dict:
        """获取粉丝

        Args:
            num:  数量
            page: 页码

        Returns:
            粉丝信息
        """
        result = (
            await Api(**API["fans"], credential=self.credential)
            .update_params(HostUin=self.euin, From=num * (page - 1), Size=num)
            .result
        )
        return {"total": result["Total"], "list": result["List"]}

    async def get_friend(self, num: int = 10, page: int = 1) -> dict:
        """获取好友

        Note:
            只根据传入的 credential 获取

        Args:
            num:  数量
            page: 页码

        Returns:
            好友信息
        """
        return await Api(**API["friend"], credential=self.credential).update_params(Page=page - 1, PageSize=num).result

    async def get_gene(self) -> dict:
        """获取音乐基因数据

        Returns:
            音乐基因数据
        """
        return await Api(**API["music_gene"], credential=self.credential).update_params(VisitAccount=self.euin).result
