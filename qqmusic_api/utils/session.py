"""Session 管理"""

import asyncio
from collections import deque
from typing import Optional, TypedDict

import httpx

from .credential import Credential
from .device import get_cached_device
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

    def __init__(self, *, credential: Optional[Credential] = None, enable_sign: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.credential = credential or Credential()
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
        self.qimei = get_qimei(get_cached_device(), self.api_config["version"])["q36"]

    async def __aenter__(self) -> "Session":
        """进入 async with 上下文时调用"""
        loop = get_loop()
        session_manager.push_to_stack(loop, self)
        await super().__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        """退出 async with 上下文时调用"""
        loop = get_loop()
        session_manager.pop_from_stack(loop)
        await super().__aexit__(*args, **kwargs)

    @property
    def musicid(self) -> int:
        """获取 musicid"""
        return self.credential.musicid

    @property
    def musickey(self) -> str:
        """获取 musickey"""
        return self.credential.musickey


class SessionManager:
    """Session 管理类,负责管理不同事件循环的 Session"""

    def __init__(self) -> None:
        """初始化 SessionManager"""
        self.session_pool: dict[asyncio.AbstractEventLoop, Session] = {}  # 存储全局 Session 池
        self.context_stack: dict[
            asyncio.AbstractEventLoop, deque[Session]
        ] = {}  # 使用 deque 存储 async with 上下文中的 Session 栈

    def get(self) -> Session:
        """获取当前事件循环的 Session"""
        loop = get_loop()
        # 优先从上下文栈中获取当前事件循环的 Session
        if self.context_stack.get(loop):
            return self.context_stack[loop][-1]
        # 如果上下文栈中没有,返回全局池中的 Session
        session = self.session_pool.get(loop, None)
        if not session:
            session = Session()
            self.session_pool[loop] = session
        return session

    def set(self, session: Session) -> None:
        """设置当前事件循环的 Session(全局池)"""
        loop = get_loop()
        # 如果当前事件循环正在 async with 中,不能直接设置 Session
        if self.context_stack.get(loop):
            raise Exception("不能在 `async with` 块中设置 Session.")
        self.session_pool[loop] = session

    def push_to_stack(self, loop: asyncio.AbstractEventLoop, session: Session) -> None:
        """将 Session 推入当前事件循环的 async with 上下文栈"""
        if loop not in self.context_stack:
            self.context_stack[loop] = deque()  # 初始化 deque
        self.context_stack[loop].append(session)

    def pop_from_stack(self, loop: asyncio.AbstractEventLoop) -> None:
        """从当前事件循环的 async with 上下文栈中弹出 Session"""
        if self.context_stack.get(loop):
            self.context_stack[loop].pop()

    def create_session(self, credential: Optional[Credential] = None, enable_sign: bool = False) -> Session:
        """创建新的 Session"""
        session = Session(credential=credential, enable_sign=enable_sign)
        self.session_pool[get_loop()] = session
        return session

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


def create_session(credential: Optional[Credential] = None, enable_sign: bool = False) -> Session:
    """创建新的 Session

    Args:
        credential: 凭据
        enable_sign: 是否启用 sign
    """
    return session_manager.create_session(credential=credential, enable_sign=enable_sign)


def set_session_credential(credential: Credential):
    """设置当前 Session 的凭据"""
    session_manager.get().credential = credential


def get_loop() -> asyncio.AbstractEventLoop:
    """获取当前事件循环"""
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()
