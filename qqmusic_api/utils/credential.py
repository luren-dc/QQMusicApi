"""凭据类，用于请求验证"""

from dataclasses import dataclass, field
from typing import Union

from qqmusic_api.exceptions import (
    CredentialNoMusicidException,
    CredentialNoMusickeyException,
    CredentialNoRefreshkeyException,
)


@dataclass
class Credential:
    """凭据类

    Attributes:
        openid:        OpenID
        refresh_token: RefreshToken
        access_token:  AccessToken
        expired_at:    到期时间
        musicid:       QQMusicID
        musickey:      QQMusicKey
        unionid:       UnionID
        str_musicid:   QQMusicID
        refresh_key:   RefreshKey
        login_type:    登录类型
        extra_fields:  额外字段
    """

    openid: str = ""
    refresh_token: str = ""
    access_token: str = ""
    expired_at: int = 0
    musicid: int = 0
    musickey: str = ""
    unionid: str = ""
    str_musicid: str = ""
    refresh_key: str = ""
    encrypt_uin: str = ""
    login_type: int = 0
    extra_fields: dict[str, Union[str, int]] = field(default_factory=dict)

    def __post_init__(self):
        if not self.login_type:
            if self.musickey and self.musickey.startswith("W_X"):
                self.login_type = 1
            else:
                self.login_type = 2

    def has_musicid(self) -> bool:
        """是否提供 musicid

        Returns:
            是否提供
        """
        return bool(self.musicid)

    def has_musickey(self) -> bool:
        """是否提供 musickey

        Returns:
            是否提供
        """
        return bool(self.musickey)

    def can_refresh(self) -> bool:
        """是否能刷新 Credential

        Returns:
            是否能刷新
        """
        return bool(self.musicid) and (bool(self.refresh_key) or bool(self.musickey))

    def raise_for_cannot_refresh(self):
        """无法刷新 Credential 时抛出异常

        Raises:
            CredentialNoRefreshkeyException
        """
        if not self.can_refresh():
            raise CredentialNoRefreshkeyException()

    def raise_for_no_musicid(self):
        """没有提供 musicid 时抛出异常

        Raises:
            CredentialNoMusicidException
        """
        if not self.has_musicid():
            raise CredentialNoMusicidException()

    def raise_for_no_musickey(self):
        """没有提供 musickey 时抛出异常"""
        if not self.has_musickey():
            raise CredentialNoMusickeyException()

    async def refresh(self):
        """刷新 cookies"""
        from ..login import refresh_cookies

        c = await refresh_cookies(self)
        self.__dict__.update(c.__dict__)

    @classmethod
    def from_cookies(cls, cookies: dict) -> "Credential":
        """从 cookies 创建 Credential 实例

        Args:
            cookies: Cookies 字典

        Returns:
            凭据类实例
        """
        return cls(
            openid=cookies.pop("openid", ""),
            refresh_token=cookies.pop("refresh_token", ""),
            access_token=cookies.pop("access_token", ""),
            expired_at=cookies.pop("expired_at", 0),
            musicid=cookies.pop("musicid", ""),
            musickey=cookies.pop("musickey", ""),
            unionid=cookies.pop("unionid", ""),
            str_musicid=cookies.pop(
                "str_musicid",
                str(cookies.pop("musicid", "")),
            ),
            refresh_key=cookies.pop("refresh_key", ""),
            encrypt_uin=cookies.pop("encryptUin", ""),
            login_type=cookies.pop("loginType", 0),
            extra_fields=cookies,
        )
