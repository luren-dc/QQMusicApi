from ..exceptions import (
    CredentialNoMusicidException,
    CredentialNoMusickeyException,
    CredientialCanNotRefreshException,
)


class Credential:
    def __init__(
        self, musicid: str = "", musickey: str = "", refresh_key: str = "", **kwagrs
    ):
        self.musicid = musicid
        self.musickey = musickey
        self.refresh_key = refresh_key
        self.login_type = 1 if "W_X" in musickey else 2

        for key, value in kwagrs.items():
            setattr(self, key, value)

    def get_dict(self) -> dict:
        cookies = {}
        for key, value in self.__dict__.items():
            if key not in cookies and value is not None:
                cookies[key] = value
        return cookies

    def has_musicid(self) -> bool:
        """
        是否提供 musicid
        """
        return bool(self.musicid)

    def has_musickey(self) -> bool:
        """
        是否提供 musickey
        """
        return bool(self.musickey)

    def can_refresh(self) -> bool:
        """
        是否能刷新 Credential
        """
        return bool(self.refresh_key)

    def raise_for_cannot_refresh(self):
        """
        无法刷新 Credential 时则抛出异常
        """
        if not self.can_refresh():
            raise CredientialCanNotRefreshException()

    def raise_for_no_musicid(self):
        """
        没有提供 musicid 时抛出异常
        """
        if not self.has_musicid():
            raise CredentialNoMusicidException()

    def raise_for_no_musickey(self):
        """
        没有提供 musickey 时抛出异常
        """
        if not self.has_musickey():
            raise CredentialNoMusickeyException()

    async def refresh(self):
        """
        刷新 cookies
        """
        from ..api.login import refresh_cookies

        c = await refresh_cookies(self)
        self.musicid = c.musicid
        self.musickey = c.musickey
        self.refresh_key = c.refresh_key

    @classmethod
    def from_cookies(cls, cookies: dict = {}) -> "Credential":
        """
        从 cookies 新建 Credential

        Args:
            cookies : Cookies.

        Returns:
            Credential: 凭据类
        """
        c = cls()
        c.musicid = cookies["musicid"]
        c.musickey = cookies["musickey"]
        c.refresh_key = cookies["refresh_key"]
        return c
