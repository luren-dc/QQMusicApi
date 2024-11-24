"""Session 管理"""

import asyncio
import sys
from collections.abc import Mapping
from typing import Any, Callable, Optional, Union

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import httpx
from httpx._client import DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG, EventHook
from httpx._types import (
    AuthTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    ProxiesTypes,
    ProxyTypes,
    QueryParamTypes,
    TimeoutTypes,
    VerifyTypes,
)

from .credential import Credential
from .qimei import QIMEI

_SESSION_POOL: dict[asyncio.AbstractEventLoop, list["Session"]] = dict()


def get_loop() -> asyncio.AbstractEventLoop:
    """获取事件循环"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    return loop


class Session(httpx.AsyncClient):
    """Session

    QQ音乐登录态 / API 请求管理

    注：Session 各 `Eventloop` 独立，利用 `async with` 设置的 Session 不互相影响
    """

    HOST = "y.qq.com"
    """QQ音乐域名"""

    UA_DEFAULT = "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54"
    """默认 User-Agent"""

    async def __aenter__(self) -> Self:
        _SESSION_POOL.setdefault(get_loop(), list())
        _SESSION_POOL[get_loop()].append(self)
        return await super().__aenter__()

    async def __aexit__(self, *args, **kwargs) -> None:
        _SESSION_POOL[get_loop()].pop()
        return await super().__aexit__(*args, **kwargs)

    def __init__(
        self,
        *,
        credential: Optional[Credential] = None,
        auth: Optional[AuthTypes] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        verify: VerifyTypes = False,
        cert: Optional[CertTypes] = None,
        http1: bool = True,
        http2: bool = False,
        proxy: Optional[ProxyTypes] = None,
        proxies: Optional[ProxiesTypes] = None,
        mounts: Optional[Mapping[str, Optional[httpx.AsyncBaseTransport]]] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        limits: httpx.Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Optional[(Mapping[str, list[EventHook]])] = None,
        base_url: Union[httpx.URL, str] = "",
        transport: Optional[httpx.AsyncBaseTransport] = None,
        app: Optional[Callable[..., Any]] = None,
        trust_env: bool = True,
        default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
    ) -> None:
        super().__init__(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            proxy=proxy,
            proxies=proxies,
            mounts=mounts,
            timeout=timeout,
            follow_redirects=follow_redirects,
            limits=limits,
            max_redirects=max_redirects,
            event_hooks=event_hooks,
            base_url=base_url,
            transport=transport,
            app=app,
            trust_env=trust_env,
            default_encoding=default_encoding,
        )

        self.headers = httpx.Headers(
            {
                "User-Agent": self.UA_DEFAULT,
                "Referer": self.HOST,
            }
        )

        self.api_config = {
            "version": "13.2.5.8",
            "version_code": 13020508,
            "qimei": QIMEI.get_qimei("13.2.5.8").q36,
        }

        self.credential = credential or Credential()

    @property
    def qimei(self) -> str:
        """获取 Qimei"""
        return str(self.api_config["qimei"])

    @property
    def musicid(self) -> int:
        """获取 musicid"""
        return self.credential.musicid

    @property
    def musickey(self) -> str:
        """获取 musickey"""
        return self.credential.musickey


class SessionManager:
    """Session 管理"""

    def __init__(self) -> None:
        self.session_pool = {get_loop(): Session()}

    def get(self) -> Session:
        """获取当前 EventLoop 的 Session"""
        if _SESSION_POOL.get(get_loop(), None):
            return _SESSION_POOL[get_loop()][-1]
        session = self.session_pool.get(get_loop(), None)
        if not session:
            session = Session()
            self.session_pool[get_loop()] = session
        return session

    def set(self, session: Session) -> None:
        """设置当前 EventLoop 的 Session"""
        if _SESSION_POOL.get(get_loop(), None):
            raise Exception("Current Session is in `async with` block, which cannot be reassigned.")
        self.session_pool[get_loop()] = session


session_manager = SessionManager()


def get_session() -> Session:
    """获取当前正在使用的 Session"""
    session = session_manager.get()
    return session


def set_session(session: Session):
    """设置当前正在使用的 Session"""
    session_manager.set(session)


def create_session(credentilal: Optional[Credential] = None) -> Session:
    """创建并返回 Session

    Args:
        credentilal: 凭证
    """
    return Session(credential=credentilal)


def set_session_credential(credential: Credential):
    """设置当前正在使用的 Session 的 Credential

    Args:
        credential: 凭证
    """
    get_session().credential = credential
