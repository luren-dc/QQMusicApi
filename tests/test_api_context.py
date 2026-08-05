"""ApiContext 核心逻辑单元测试 (桩会话驱动, 不发起真实网络)."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

import niquests
import pytest
import pytest_asyncio

from qqmusic_api.core.api_context import ApiContext
from qqmusic_api.core.versioning import Platform

if TYPE_CHECKING:
    from niquests import AsyncSession

pytestmark = pytest.mark.core


class DummyResponse:
    """模拟 niquests 响应对象的最小桩."""

    def __init__(
        self,
        payload: Any,
        status_code: int = 200,
        *,
        content: bytes | None = b"{}",
        json_error: bool = False,
        http_error: bool = False,
    ) -> None:
        """以预置载荷与可选状态码构造响应桩.

        Args:
            payload: 供 json() 返回的载荷.
            status_code: HTTP 状态码.
            content: 原始响应体, 用于触发 "响应无内容" 分支.
            json_error: 是否让 json() 抛出解析异常.
            http_error: 是否让 raise_for_status() 抛出 HTTP 状态异常.
        """
        self._payload = payload
        self.status_code = status_code
        self.content = content
        self.text = ""
        self._json_error = json_error
        self._http_error = http_error

    def json(self) -> Any:
        """按预置标记返回载荷或抛出解析异常."""
        if self._json_error:
            raise ValueError("模拟 JSON 解析失败")
        return self._payload

    def raise_for_status(self) -> None:
        """按预置标记抛出 HTTP 状态异常."""
        if self._http_error:
            raise niquests.HTTPError(f"HTTP {self.status_code}")


class StubSession:
    """记录 post/request 调用并按队列返回预置响应的会话桩."""

    def __init__(self, posts: list[Any] | None = None, requests: list[Any] | None = None) -> None:
        """以预置的 CGI 与 HTTP 响应/异常队列构造会话桩."""
        self.post_calls: list[tuple[str, dict[str, Any]]] = []
        self.request_calls: list[tuple[str, str, dict[str, Any]]] = []
        self._posts = list(posts or [])
        self._requests = list(requests or [])

    async def post(self, url: str, **kwargs: Any) -> DummyResponse:
        """记录 CGI 调用并返回或抛出下一个预置项."""
        self.post_calls.append((url, kwargs))
        if not self._posts:
            raise AssertionError(f"CGI 会话桩队列耗尽, 意外网络调用: {url}")
        item = self._posts.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    async def request(self, method: str, url: str, **kwargs: Any) -> DummyResponse:
        """记录 HTTP 调用并返回或抛出下一个预置项."""
        self.request_calls.append((method, url, kwargs))
        if not self._requests:
            raise AssertionError(f"HTTP 会话桩队列耗尽, 意外网络调用: {method} {url}")
        item = self._requests.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    async def gather(self, *responses: Any) -> None:
        """收集响应, 测试桩中为空操作."""

    async def close(self) -> None:
        """关闭会话, 测试桩中为空操作."""


class StubQimeiManager:
    """返回固定 QIMEI 字典的桩管理器 (避免真实网络调用)."""

    async def get_cached(self) -> dict[str, str]:
        """返回固定 QIMEI 字典, 供 build_comm 以下标访问 q16/q36."""
        return {"q16": "test_q16_value", "q36": "test_q36_value"}


@dataclass
class StubContext:
    """ApiContext 与其默认桩会话的测试载体."""

    context: ApiContext
    stub: StubSession


@pytest_asyncio.fixture
async def stub_context() -> AsyncIterator[StubContext]:
    """创建使用 Web 平台且不触网的最小 ApiContext 测试载体."""
    stub = StubSession()
    context = ApiContext(
        session=cast("AsyncSession", stub),
        platform=Platform.WEB,
        device_path=None,
    )
    # 覆盖内部 QIMEI 管理器为桩, 防止 Android 路径触发真实网络调用.
    cast("Any", context)._qimei_manager = StubQimeiManager()
    yield StubContext(context=context, stub=stub)


async def test_get_user_agent_android(stub_context: StubContext) -> None:
    """验证 Android 平台生成期望的 QQMusic UA 字符串."""
    ua = await stub_context.context.get_user_agent(Platform.ANDROID)
    assert ua == "QQMusic 14090008(android 10)"


async def test_get_user_agent_web_desktop(stub_context: StubContext) -> None:
    """验证 WEB 与 DESKTOP 平台返回相同的 Chrome UA 字符串."""
    web_ua = await stub_context.context.get_user_agent(Platform.WEB)
    desktop_ua = await stub_context.context.get_user_agent(Platform.DESKTOP)
    assert web_ua == desktop_ua
    assert web_ua == (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )


async def test_get_user_agent_default_platform(stub_context: StubContext) -> None:
    """验证不传平台参数时使用上下文默认平台生成 UA."""
    ua = await stub_context.context.get_user_agent()
    assert ua == (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )


@pytest.mark.parametrize(
    ("musicid", "str_musicid", "expected_uin"),
    [
        (123, "", "123"),
        (123, "456", "456"),
    ],
)
async def test_prepare_http_kwargs_injects_cookies(
    stub_context: StubContext, musicid: int, str_musicid: str, expected_uin: str
) -> None:
    """验证凭证注入 Cookies 且 str_musicid 优先于 musicid."""
    from qqmusic_api.models.request import Credential

    credential = Credential(musicid=musicid, str_musicid=str_musicid, musickey="key")
    result = await stub_context.context.prepare_http_kwargs(credential=credential)
    cookies = result["cookies"]
    assert cookies["uin"] == expected_uin
    assert cookies["qqmusic_uin"] == expected_uin
    assert cookies["qm_keyst"] == "key"
    assert cookies["qqmusic_key"] == "key"


async def test_prepare_http_kwargs_user_cookies_override(stub_context: StubContext) -> None:
    """验证用户传入的 cookies 覆盖凭证注入的同名键."""
    from qqmusic_api.models.request import Credential

    result = await stub_context.context.prepare_http_kwargs(
        credential=Credential(musicid=123, musickey="key"),
        cookies={"uin": "custom", "extra": "x"},
    )
    cookies = result["cookies"]
    assert cookies["uin"] == "custom"
    assert cookies["extra"] == "x"
    assert cookies["qm_keyst"] == "key"


async def test_prepare_http_kwargs_no_credential(stub_context: StubContext) -> None:
    """验证无凭证时不注入 cookies 且补全 WEB 平台 UA."""
    result = await stub_context.context.prepare_http_kwargs()
    assert "cookies" not in result
    assert result["headers"]["User-Agent"] == (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )


async def test_prepare_http_kwargs_respects_existing_ua(stub_context: StubContext) -> None:
    """验证已存在的 User-Agent 不被覆盖."""
    result = await stub_context.context.prepare_http_kwargs(headers={"User-Agent": "custom-ua"})
    assert result["headers"]["User-Agent"] == "custom-ua"


async def test_ensure_session_non_android_noop(stub_context: StubContext) -> None:
    """验证非 Android 平台调用 ensure_session 不发起任何网络请求."""
    await stub_context.context.ensure_session(Platform.DESKTOP)
    assert stub_context.stub.post_calls == []


async def test_ensure_session_valid_session_short_circuit(stub_context: StubContext) -> None:
    """验证设备已有有效会话时短路返回且不触网不改写字段."""
    import time

    context = stub_context.context
    device = await cast("Any", context)._device_store.get_device()
    device.session_uid = "1"
    device.session_sid = "s"
    device.session_save_time = int(time.time())
    await context.ensure_session(Platform.ANDROID)
    assert stub_context.stub.post_calls == []
    assert device.session_uid == "1"
    assert device.session_sid == "s"
    assert device.session_save_time is not None


async def test_ensure_session_invalid_session_posts_and_updates_device(stub_context: StubContext) -> None:
    """验证无效会话时发起 CGI 请求并将响应写回设备会话字段."""
    context = stub_context.context
    fresh_stub = StubSession(
        posts=[DummyResponse({"req_0": {"data": {"session": {"uid": "1", "sid": "s", "vkey": "v"}}}})]
    )
    cast("Any", context)._session = fresh_stub
    await context.ensure_session(Platform.ANDROID)
    assert fresh_stub.post_calls[0][0] == "https://u.y.qq.com/cgi-bin/musicu.fcg"
    device = await cast("Any", context)._device_store.get_device()
    assert device.session_uid == "1"
    assert device.session_sid == "s"
    assert device.session_vkey == "v"
    assert device.session_save_time is not None


async def test_ensure_session_network_error(stub_context: StubContext) -> None:
    """验证底层请求异常被转换为 NetworkError 抛出."""
    from niquests.exceptions import RequestException

    from qqmusic_api.core.exceptions import NetworkError

    context = stub_context.context
    fresh_stub = StubSession(posts=[RequestException("boom")])
    cast("Any", context)._session = fresh_stub
    with pytest.raises(NetworkError):
        await context.ensure_session(Platform.ANDROID)


async def test_ensure_session_http_error(stub_context: StubContext) -> None:
    """验证非 200 状态码响应被转换为 HTTPError 抛出."""
    from qqmusic_api.core.exceptions import HTTPError

    context = stub_context.context
    fresh_stub = StubSession(posts=[DummyResponse({}, status_code=500)])
    cast("Any", context)._session = fresh_stub
    with pytest.raises(HTTPError) as exc_info:
        await context.ensure_session(Platform.ANDROID)
    assert exc_info.value.status_code == 500
    assert "500" in str(exc_info.value)


async def test_build_api_kwargs_web_no_session_no_qimei(stub_context: StubContext) -> None:
    """验证 WEB 平台构建默认 comm 且不触发任何网络请求."""
    url, payload, params, headers = await stub_context.context.build_api_kwargs(
        data=[{"module": "test", "method": "test", "param": {}}]
    )
    assert url == "https://u.y.qq.com/cgi-bin/musicu.fcg"
    assert payload["comm"]["ct"] == 24
    assert payload["comm"]["cv"] == 4747474
    assert payload["comm"]["platform"] == "yqq.json"
    assert "g_tk" in payload["comm"]
    assert payload["comm"]["format"] == "json"
    assert payload["req_0"] == {"module": "test", "method": "test", "param": {}}
    assert "req_1" not in payload
    assert params == {}
    assert headers["User-Agent"] == (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    assert stub_context.stub.post_calls == []


async def test_build_api_kwargs_android_includes_qimei_and_session() -> None:
    """验证 Android 平台 comm 包含 QIMEI 与设备会话字段且不触网."""
    import time

    stub = StubSession()
    ctx = ApiContext(
        session=cast("AsyncSession", stub),
        platform=Platform.ANDROID,
        device_path=None,
    )
    cast("Any", ctx)._qimei_manager = StubQimeiManager()
    device = await cast("Any", ctx)._device_store.get_device()
    device.session_uid = "1"
    device.session_sid = "s"
    device.session_save_time = int(time.time())
    _, payload, _, _ = await ctx.build_api_kwargs(data=[{"module": "m", "method": "m", "param": {}}])
    assert payload["comm"]["QIMEI"] == "test_q16_value"
    assert payload["comm"]["QIMEI36"] == "test_q36_value"
    assert payload["comm"]["OpenUDID"] == device.open_udid
    assert payload["comm"]["uid"] == "1"
    assert payload["comm"]["sid"] == "s"
    assert stub.post_calls == []


async def test_build_api_kwargs_override_comm(stub_context: StubContext) -> None:
    """验证 override_comm 时 comm 完全替换为自定义参数."""
    _, payload, _, _ = await stub_context.context.build_api_kwargs(
        data=[{"module": "m", "method": "m", "param": {}}],
        comm={"custom": "x"},
        override_comm=True,
    )
    assert payload["comm"] == {"custom": "x"}


async def test_build_api_kwargs_comm_merge_user_wins(stub_context: StubContext) -> None:
    """验证用户 comm 合并时覆盖同名键并保留默认键."""
    _, payload, _, _ = await stub_context.context.build_api_kwargs(
        data=[{"module": "m", "method": "m", "param": {}}],
        comm={"cv": 999, "extra": "y"},
    )
    assert payload["comm"]["cv"] == 999
    assert payload["comm"]["extra"] == "y"
    assert payload["comm"]["ct"] == 24


async def test_build_api_kwargs_sign(stub_context: StubContext) -> None:
    """验证签名模式切换 URL 并生成时间戳与 zzc 签名."""
    import orjson as json

    from qqmusic_api.algorithms import zzc_sign

    url, payload, params, _ = await stub_context.context.build_api_kwargs(
        data=[{"module": "m", "method": "m", "param": {}}],
        sign=True,
    )
    assert url == "https://u.y.qq.com/cgi-bin/musics.fcg"
    assert int(params["_"]) > 0
    assert params["sign"] == zzc_sign(json.dumps(payload))


async def test_build_api_kwargs_multiple_data(stub_context: StubContext) -> None:
    """验证多个请求子项按顺序写入 req_0 与 req_1."""
    item1 = {"module": "m", "method": "m", "param": {}}
    item2 = {"module": "m2", "method": "m2", "param": {"x": 1}}
    _, payload, _, _ = await stub_context.context.build_api_kwargs(data=[item1, item2])
    assert payload["req_0"] == item1
    assert payload["req_1"] == item2
