"""凭据类,用于请求验证"""

import json
import sys
from dataclasses import asdict, dataclass, field
from typing import Any

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from ..exceptions import CredentialInvalidError


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
    extra_fields: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.login_type:
            if self.musickey and self.musickey.startswith("W_X"):
                self.login_type = 1
            else:
                self.login_type = 2

    def has_musicid(self) -> bool:
        """是否提供 musicid"""
        return bool(self.musicid)

    def has_musickey(self) -> bool:
        """是否提供 musickey"""
        return bool(self.musickey)

    def raise_for_invalid(self) -> None:
        """检查凭据是否有效

        Raises:
            CredentialInvalidError: 没有提供 musicid 或 musickey
        """
        if not self.has_musicid():
            raise CredentialInvalidError("没有提供 musicid")

        if not self.has_musickey():
            raise CredentialInvalidError("没有提供 musickey")

    async def refresh(self) -> bool:
        """刷新 cookies

        Returns:
            是否刷新成功
        """
        from ..login import refresh_cookies

        c = await refresh_cookies(self)
        if c == self:
            return False
        self.__dict__.update(c.__dict__)
        return True

    async def can_refresh(self) -> bool:
        """是否可以刷新 credential"""
        if not self.has_musicid() or not self.has_musickey():
            return False
        if await self.is_expired():
            return bool(self.refresh_key) and bool(self.refresh_token)
        return True

    async def is_expired(self) -> bool:
        """判断 credential 是否过期

        Returns:
            是否过期
        """
        from ..login import check_expired

        return await check_expired(self)

    def as_dict(self) -> dict:
        """获取凭据字典"""
        d = asdict(self)
        d["loginType"] = d.pop("login_type")
        d["encryptUin"] = d.pop("encrypt_uin")
        return d

    def as_json(self) -> str:
        """获取凭据 JSON 字符串"""
        data = self.as_dict()
        data.update(data.pop("extra_fields"))
        return json.dumps(data, indent=4, ensure_ascii=False)

    @classmethod
    def from_cookies_dict(cls, cookies: dict[str, Any]) -> Self:
        """从 cookies 字典创建 Credential 实例

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
            musicid=cookies.pop("musicid", 0),
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

    @classmethod
    def from_cookies_str(cls, cookies: str) -> Self:
        """从 cookies 字符串创建 Credential 实例

        Args:
            cookies: Cookies 字符串

        Returns:
            凭据类实例
        """
        return cls.from_cookies_dict(json.loads(cookies))
