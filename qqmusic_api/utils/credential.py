"""凭据类，用于请求验证"""

from dataclasses import asdict, dataclass, field
from typing import Any

from qqmusic_api.exceptions import (
    CredentialNoMusicidException,
    CredentialNoMusickeyException,
    CredentialNoRefreshkeyException,
)


@dataclass
class Credential:
    """凭据类

    Attributes:
        musicid: 音乐 ID
        musickey: 音乐 Key
        refresh_key: 刷新 Key
        login_type: 登录类型
        extra_fields: 额外字段
    """

    musicid: str = ""
    musickey: str = ""
    refresh_key: str = ""
    login_type: int = field(init=False)
    extra_fields: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.login_type = 1 if "W_X" in self.musickey else 2

    def get_dict(self) -> dict:
        """返回 Credential 的字典表示，包括所有字段。"""
        return {**asdict(self), **self.extra_fields}

    def has_musicid(self) -> bool:
        """是否提供 musicid"""
        return bool(self.musicid)

    def has_musickey(self) -> bool:
        """是否提供 musickey"""
        return bool(self.musickey)

    def can_refresh(self) -> bool:
        """是否能刷新 Credential"""
        return bool(self.refresh_key)

    def raise_for_cannot_refresh(self):
        """无法刷新 Credential 时抛出异常"""
        if not self.can_refresh():
            raise CredentialNoRefreshkeyException()

    def raise_for_no_musicid(self):
        """没有提供 musicid 时抛出异常"""
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
        self.musicid = c.musicid
        self.musickey = c.musickey
        self.refresh_key = c.refresh_key

    @classmethod
    def from_cookies(cls, cookies: dict) -> "Credential":
        """从 cookies 创建 Credential 实例

        Args:
            cookies: Cookies 字典

        Returns:
            凭据类实例
        """
        return cls(
            musicid=cookies.pop("musicid", ""),
            musickey=cookies.pop("musickey", ""),
            refresh_key=cookies.pop("refresh_key", ""),
            extra_fields=cookies,
        )
