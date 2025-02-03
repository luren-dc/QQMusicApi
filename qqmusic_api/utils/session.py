"""Session 管理"""

import asyncio
import ssl
from collections import deque
from collections.abc import Callable, Mapping
from typing import TypedDict

import httpx
from httpx._client import EventHook
from httpx._config import (
    DEFAULT_LIMITS,
    DEFAULT_MAX_REDIRECTS,
    DEFAULT_TIMEOUT_CONFIG,
    Limits,
)
from httpx._transports.base import AsyncBaseTransport
from httpx._types import (
    AuthTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    ProxyTypes,
    QueryParamTypes,
    TimeoutTypes,
)
from httpx._urls import URL

from .credential import Credential
from .device import get_cached_device, save_device
from .qimei import get_qimei


class ApiConfig(TypedDict):
    """API 配置"""

    version: str
    version_code: int
    enable_sign: bool
    endpoint: str
    enc_endpoint: str


class Session(httpx.AsyncClient):
    """Session 类,用于管理 QQ 音乐的登录态和 API 请求"""

    HOST = "y.qq.com"
    UA_DEFAULT = "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54"

    def __init__(
        self,
        *,
        credential: Credential | None = None,
        enable_sign: bool = False,
        auth: AuthTypes | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        cert: CertTypes | None = None,
        http1: bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        mounts: None | (Mapping[str, AsyncBaseTransport | None]) = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: None | (Mapping[str, list[EventHook]]) = None,
        base_url: URL | str = "",
        transport: AsyncBaseTransport | None = None,
        trust_env: bool = True,
        default_encoding: str | Callable[[bytes], str] = "utf-8",
    ) -> None:
        super().__init__(
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            proxy=proxy,
            mounts=mounts,
            timeout=timeout,
            follow_redirects=follow_redirects,
            limits=limits,
            max_redirects=max_redirects,
            event_hooks=event_hooks,
            base_url=base_url,
            transport=transport,
            trust_env=trust_env,
            default_encoding=default_encoding,
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
        )
        self.credential = credential
        self.headers = httpx.Headers(
            {
                "User-Agent": self.UA_DEFAULT,
                "Referer": self.HOST,
            }
        )
        self.timeout = 20
        self.api_config = ApiConfig(
            version="13.2.5.8",
            version_code=13020508,
            enable_sign=enable_sign,
            endpoint="https://u.y.qq.com/cgi-bin/musicu.fcg",
            enc_endpoint="https://u.y.qq.com/cgi-bin/musics.fcg",
        )
        device = get_cached_device()
        self.qimei = get_qimei(device, self.api_config["version"])["q36"]
        device.qimei = self.qimei
        save_device(device)

    def active(self):
        """激活 Session"""
        loop = get_loop()
        session_manager.push_to_stack(loop, self)

    def deactive(self):
        """停用 Session"""
        loop = get_loop()
        session_manager.pop_from_stack(loop)

    async def __aenter__(self) -> "Session":
        """进入 async with 上下文时调用"""
        self.active()
        await super().__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        """退出 async with 上下文时调用"""
        self.deactive()
        await super().__aexit__(*args, **kwargs)


class SessionManager:
    """Session 管理类,负责管理不同事件循环的 Session"""

    def __init__(self) -> None:
        """初始化 SessionManager"""
        self.session_pool: dict[asyncio.AbstractEventLoop, Session] = {}
        self.context_stack: dict[asyncio.AbstractEventLoop, deque[Session]] = {}

    def get(self) -> Session:
        """获取当前事件循环的 Session"""
        loop = get_loop()
        # 优先从上下文栈中获取当前事件循环的 Session
        if self.context_stack.get(loop, None):
            return self.context_stack[loop][-1]

        # 如果上下文栈中没有,返回全局池中的 Session
        session = self.session_pool.get(loop, None)
        if not session:
            session = Session()
            self.session_pool[loop] = session
        return session

    def set(self, session: Session) -> None:
        """设置当前事件循环的 Session"""
        loop = get_loop()
        # 如果当前事件循环正在 async with 中,不能直接设置 Session
        if self.context_stack.get(loop):
            raise Exception("不能在 `async with` 块中设置 Session.")
        self.session_pool[loop] = session

    def push_to_stack(self, loop: asyncio.AbstractEventLoop, session: Session) -> None:
        """将 Session 推入当前事件循环的 async with 上下文栈"""
        if loop not in self.context_stack:
            self.context_stack[loop] = deque()
        self.context_stack[loop].append(session)

    def pop_from_stack(self, loop: asyncio.AbstractEventLoop) -> None:
        """从当前事件循环的 async with 上下文栈中弹出 Session"""
        if self.context_stack.get(loop):
            self.context_stack[loop].pop()

    def reset(self) -> None:
        """重置当前事件循环的 Session"""
        loop = get_loop()
        self.session_pool.pop(loop, None)
        self.context_stack.pop(loop, None)


# 全局 Session 管理器实例
session_manager = SessionManager()


def get_session() -> Session:
    """获取当前事件循环的 Session"""
    return session_manager.get()


def set_session(session: Session) -> None:
    """设置当前事件循环的 Session"""
    session_manager.set(session)


def get_loop() -> asyncio.AbstractEventLoop:
    """获取当前事件循环"""
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()
