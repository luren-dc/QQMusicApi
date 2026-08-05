"""Client 核心逻辑单元测试 (桩会话驱动, 不发起真实网络)."""

from collections.abc import AsyncIterator
from typing import Any, cast

import niquests
import pytest
import pytest_asyncio
from niquests.exceptions import RequestException
from pydantic import BaseModel

from qqmusic_api import Client, Credential
from qqmusic_api.core.exceptions import ApiDataError, CredentialInvalidError, NetworkError
from qqmusic_api.core.request import BaseRequest, CgiRequest, HttpRequest
from qqmusic_api.core.versioning import Platform

pytestmark = pytest.mark.core


class DummyModel(BaseModel):
    """测试用 Pydantic 响应模型."""

    value: int


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


def _cgi_response(sub_payloads: list[dict[str, Any]]) -> DummyResponse:
    """构造包含多个子响应的 CGI 批量响应桩."""
    payload: dict[str, Any] = {"code": 0}
    for idx, sub in enumerate(sub_payloads):
        payload[f"req_{idx}"] = sub
    return DummyResponse(payload)


def _cgi_sub(code: int = 0, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """构造单个 CGI 子响应字典."""
    return {"code": code, "data": data or {}}


def _cgi_request(client: Client, param: dict[str, Any] | None = None, **kwargs: Any) -> CgiRequest[Any]:
    """构造测试用 CGI 请求描述符."""
    return CgiRequest(_client=client, module="test", method="test", param=param or {}, **kwargs)


def _http_request(client: Client, url: str = "https://example.com", **kwargs: Any) -> HttpRequest[Any]:
    """构造测试用 HTTP 请求描述符."""
    return HttpRequest(_client=client, method="GET", url=url, **kwargs)


def _attach_session(client: Client, stub: StubSession) -> None:
    """将桩会话注入客户端, 请求上下文与 QIMEI 管理器以替换真实网络会话."""
    cast("Any", client)._session = stub
    cast("Any", client)._context._session = stub
    cast("Any", client)._context._qimei_manager._session = stub


@pytest_asyncio.fixture
async def stub_client() -> AsyncIterator[Client]:
    """创建使用 Web 平台且不触网的最小 Client 实例."""
    test_client = Client(platform=Platform.WEB)
    # 真实 AsyncSession 在构造时即被创建, 保存引用以便测试结束时显式关闭.
    real_session = cast("Any", test_client)._session
    yield test_client
    await test_client.close()
    await real_session.close()


async def test_gather_returns_results_in_input_order(stub_client: Client):
    """测试 gather 结果顺序与传入请求顺序一致."""
    stub = StubSession(posts=[_cgi_response([_cgi_sub(data={"value": 1}), _cgi_sub(data={"value": 2})])])
    _attach_session(stub_client, stub)
    reqs: list[BaseRequest[Any]] = [
        _cgi_request(stub_client, response_model=DummyModel),
        _cgi_request(stub_client, response_model=DummyModel),
    ]
    results = await stub_client.gather(reqs)
    assert [r.value for r in results] == [1, 2]


async def test_gather_merges_same_group_into_one_call(stub_client: Client):
    """测试同组 CGI 请求合并为一次多参数调用."""
    stub = StubSession(posts=[_cgi_response([_cgi_sub(), _cgi_sub()])])
    _attach_session(stub_client, stub)
    reqs: list[BaseRequest[Any]] = [_cgi_request(stub_client), _cgi_request(stub_client)]
    await stub_client.gather(reqs)
    assert len(stub.post_calls) == 1
    payload = stub.post_calls[0][1]["json"]
    assert "req_0" in payload
    assert "req_1" in payload


async def test_gather_batch_size_splits_group(stub_client: Client):
    """测试 batch_size 将同组请求拆分为多次批量调用."""
    stub = StubSession(posts=[_cgi_response([_cgi_sub()]), _cgi_response([_cgi_sub()])])
    _attach_session(stub_client, stub)
    reqs: list[BaseRequest[Any]] = [_cgi_request(stub_client), _cgi_request(stub_client)]
    await stub_client.gather(reqs, batch_size=1)
    assert len(stub.post_calls) == 2
    for _, kwargs in stub.post_calls:
        assert set(kwargs["json"]) == {"comm", "req_0"}


async def test_gather_separates_groups_by_credential(stub_client: Client):
    """测试凭证不同的 CGI 请求分属不同分组."""
    stub = StubSession(posts=[_cgi_response([_cgi_sub()]), _cgi_response([_cgi_sub()])])
    _attach_session(stub_client, stub)
    reqs: list[BaseRequest[Any]] = [
        _cgi_request(stub_client, credential=Credential(musicid=1, musickey="a")),
        _cgi_request(stub_client, credential=Credential(musicid=2, musickey="b")),
    ]
    await stub_client.gather(reqs)
    assert len(stub.post_calls) == 2


async def test_gather_http_requests_not_merged(stub_client: Client):
    """测试 HTTP 请求不合并, 各自独立执行."""
    stub = StubSession(requests=[DummyResponse({"ok": True}), DummyResponse({"ok": False})])
    _attach_session(stub_client, stub)
    reqs: list[BaseRequest[Any]] = [_http_request(stub_client), _http_request(stub_client)]
    results = await stub_client.gather(reqs)
    assert len(stub.request_calls) == 2
    assert [r["ok"] for r in results] == [True, False]


async def test_gather_mixed_protocols(stub_client: Client):
    """测试 CGI 与 HTTP 请求混合时按协议并行执行."""
    stub = StubSession(
        posts=[_cgi_response([_cgi_sub(data={"value": 1})])],
        requests=[DummyResponse({"ok": True})],
    )
    _attach_session(stub_client, stub)
    reqs: list[BaseRequest[Any]] = [
        _cgi_request(stub_client, response_model=DummyModel),
        _http_request(stub_client),
    ]
    results = await stub_client.gather(reqs)
    assert len(stub.post_calls) == 1
    assert len(stub.request_calls) == 1
    assert results[0] == DummyModel(value=1)
    assert results[1] == {"ok": True}


async def test_gather_return_exceptions_true_places_error(stub_client: Client):
    """测试 return_exceptions 为 True 时失败项以异常对象出现在对应位置."""
    stub = StubSession(
        posts=[
            RequestException("boom"),
            _cgi_response([_cgi_sub(data={"value": 2})]),
        ]
    )
    _attach_session(stub_client, stub)
    reqs: list[BaseRequest[Any]] = [
        _cgi_request(stub_client, credential=Credential(musicid=1, musickey="a"), response_model=DummyModel),
        _cgi_request(stub_client, credential=Credential(musicid=2, musickey="b"), response_model=DummyModel),
    ]
    results = await stub_client.gather(reqs, return_exceptions=True)
    assert isinstance(results[0], NetworkError)
    assert results[1] == DummyModel(value=2)


async def test_gather_return_exceptions_false_raises_group(stub_client: Client):
    """测试 return_exceptions 为 False 时以异常组形式抛出."""
    stub = StubSession(posts=[RequestException("boom")])
    _attach_session(stub_client, stub)
    reqs: list[BaseRequest[Any]] = [_cgi_request(stub_client)]
    # anyio task group 将普通异常包装为 ExceptionGroup (BaseExceptionGroup 子类).
    with pytest.raises(Exception, match="unhandled errors in a TaskGroup"):
        await stub_client.gather(reqs)


async def test_gather_parse_failure_backfills_when_return_exceptions(stub_client: Client):
    """测试响应解析失败时 return_exceptions 回填异常对象."""
    stub = StubSession(posts=[_cgi_response([_cgi_sub()])])
    _attach_session(stub_client, stub)
    reqs: list[BaseRequest[Any]] = [_cgi_request(stub_client), _cgi_request(stub_client)]
    results = await stub_client.gather(reqs, return_exceptions=True)
    assert isinstance(results[0], ApiDataError)
    assert isinstance(results[1], ApiDataError)


async def test_gather_invalid_batch_size_raises_value_error(stub_client: Client):
    """测试 batch_size 小于等于 0 时抛出 ValueError."""
    reqs: list[BaseRequest[Any]] = [_cgi_request(stub_client)]
    with pytest.raises(ValueError, match="batch_size"):
        await stub_client.gather(reqs, batch_size=0)


async def test_gather_empty_returns_empty_list(stub_client: Client):
    """测试空请求列表返回空列表."""
    assert await stub_client.gather([]) == []


async def test_execute_network_error_converted(stub_client: Client):
    """测试 execute 将网络异常转换为 NetworkError."""
    stub = StubSession(posts=[RequestException("boom")])
    _attach_session(stub_client, stub)
    with pytest.raises(NetworkError):
        await stub_client.execute(_cgi_request(stub_client))


async def test_execute_require_login_without_credential_raises(stub_client: Client):
    """测试 require_login 请求缺少凭证时抛出 CredentialInvalidError."""
    with pytest.raises(CredentialInvalidError):
        await stub_client.execute(_cgi_request(stub_client, require_login=True))


async def test_execute_http_uses_request_credential(stub_client: Client):
    """测试 HTTP 请求使用自身的凭证注入 Cookie."""
    stub = StubSession(requests=[DummyResponse({"ok": True})])
    _attach_session(stub_client, stub)
    cred = Credential(musicid=123, musickey="key")
    await stub_client.execute(_http_request(stub_client, credential=cred))
    cookies = stub.request_calls[0][2].get("cookies", {})
    assert cookies["uin"] == "123"
    assert cookies["qm_keyst"] == "key"


async def test_execute_cgi_http_status_error(stub_client: Client):
    """测试 execute 遇到非 200 状态码时抛出 HTTPError."""
    from qqmusic_api.core.exceptions import HTTPError

    stub = StubSession(posts=[DummyResponse({}, status_code=500)])
    _attach_session(stub_client, stub)
    with pytest.raises(HTTPError, match="500"):
        await stub_client.execute(_cgi_request(stub_client))


async def test_execute_cgi_global_api_error(stub_client: Client):
    """测试 execute 遇到非零全局 code 时抛出 GlobalApiError."""
    from qqmusic_api.core.exceptions import GlobalApiError

    stub = StubSession(posts=[DummyResponse({"code": -400, "req_0": {}})])
    _attach_session(stub_client, stub)
    with pytest.raises(GlobalApiError):
        await stub_client.execute(_cgi_request(stub_client))


async def test_execute_cgi_json_parse_error(stub_client: Client):
    """测试 execute 遇到响应 JSON 解析失败时抛出 ApiDataError."""
    stub = StubSession(posts=[DummyResponse({}, json_error=True)])
    _attach_session(stub_client, stub)
    with pytest.raises(ApiDataError, match="JSON"):
        await stub_client.execute(_cgi_request(stub_client))


async def test_execute_cgi_empty_response(stub_client: Client):
    """测试 execute 遇到无内容响应时抛出 ApiDataError."""
    stub = StubSession(posts=[DummyResponse({}, content=b"")])
    _attach_session(stub_client, stub)
    with pytest.raises(ApiDataError, match="响应无内容"):
        await stub_client.execute(_cgi_request(stub_client))


async def test_execute_cgi_missing_req_key(stub_client: Client):
    """测试 execute 遇到缺少预期子响应键时抛出 ApiDataError."""
    stub = StubSession(posts=[DummyResponse({"req_9": {}})])
    _attach_session(stub_client, stub)
    with pytest.raises(ApiDataError, match="CGI 响应格式异常"):
        await stub_client.execute(_cgi_request(stub_client))
