"""分页与换一批策略单元测试."""

from typing import Any, cast

import pytest
from pydantic import BaseModel

from qqmusic_api.core.pagination import (
    BatchRefreshStrategy,
    CursorStrategy,
    MultiFieldContinuationStrategy,
    OffsetStrategy,
    PageStrategy,
)
from qqmusic_api.core.request import PaginatedRequest, RefreshableRequest


class DummyResponse(BaseModel):
    """测试用简单响应结构."""

    has_more: bool | None = None
    total: int | None = None
    items: list[Any] | None = None
    next_cursor: str | None = None


def test_page_strategy_has_next_and_next_params():
    """测试基于页码的分页策略 has_next 与 next_params."""
    strategy = PageStrategy[Any, DummyResponse](
        page_key="page",
        page_size=10,
        start_page=1,
        total_extractor=lambda r: r.total,
        has_more_extractor=lambda r: r.has_more,
    )
    # 当 has_more 显式提供时
    resp_flag = DummyResponse(has_more=True)
    assert strategy.has_next({"page": 1}, resp_flag) is True

    resp_no_flag = DummyResponse(has_more=False)
    assert strategy.has_next({"page": 1}, resp_no_flag) is False

    # 根据 total 判断
    resp_total = DummyResponse(has_more=None, total=25)
    assert strategy.has_next({"page": 1}, resp_total) is True
    assert strategy.has_next({"page": 3}, resp_total) is False

    # next_params 增量
    next_p = strategy.next_params({"page": 1}, resp_total)
    assert next_p["page"] == 2


def test_offset_strategy_has_next_and_next_params():
    """测试基于偏移量的分页策略 has_next 与 next_params."""
    strategy = OffsetStrategy[Any, DummyResponse](
        offset_key="start",
        page_size_key="size",
        start_offset=0,
        total_extractor=lambda r: r.total,
        count_extractor=lambda r: len(r.items) if r.items is not None else None,
    )

    resp = DummyResponse(total=30, items=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    params = {"start": 0, "size": 10}

    assert strategy.has_next(params, resp) is True

    next_p = strategy.next_params(params, resp)
    assert next_p["start"] == 10

    # 到底部
    last_params = {"start": 20, "size": 10}
    last_resp = DummyResponse(total=30, items=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert strategy.has_next(last_params, last_resp) is False


def test_batch_refresh_strategy():
    """测试换一批策略 has_next 与 next_params."""
    strategy = BatchRefreshStrategy[Any, DummyResponse](
        refresh_key="vec",
        cursor_extractor=lambda r: r.next_cursor,
        has_more_extractor=lambda r: r.has_more,
    )

    resp_more = DummyResponse(has_more=True, next_cursor="cur2")
    params = {"vec": "cur1"}

    assert strategy.has_next(params, resp_more) is True
    assert strategy.next_params(params, resp_more) == {"vec": "cur2"}

    # 当 has_more 为 None 但游标不同
    resp_none = DummyResponse(has_more=None, next_cursor="cur2")
    assert strategy.has_next(params, resp_none) is True

    # 游标相同
    same_params = {"vec": "cur2"}
    assert strategy.has_next(same_params, resp_more) is False


def test_cursor_strategy():
    """测试游标策略 has_next 与 next_params."""
    strategy = CursorStrategy[Any, DummyResponse](
        cursor_key="pos",
        cursor_extractor=lambda r: r.next_cursor,
        has_more_extractor=lambda r: r.has_more,
    )

    resp = DummyResponse(has_more=True, next_cursor="100")
    params = {"pos": "0"}

    assert strategy.has_next(params, resp) is True
    assert strategy.next_params(params, resp) == {"pos": "100"}


def test_multi_field_continuation_strategy():
    """测试多字段延续策略 has_next 与 next_params."""

    def builder(p: dict[str, Any], r: DummyResponse) -> dict[str, Any] | None:
        if not r.items:
            return None
        return {**p, "page": p.get("page", 1) + 1}

    strategy = MultiFieldContinuationStrategy[Any, DummyResponse](builder)

    resp_has = DummyResponse(items=[1, 2])
    resp_empty = DummyResponse(items=[])

    params = {"page": 1}
    assert strategy.has_next(params, resp_has) is True
    assert strategy.next_params(params, resp_has) == {"page": 2}

    assert strategy.has_next(params, resp_empty) is False
    with pytest.raises(ValueError, match="分页响应未提供继续翻页所需的 continuation 数据"):
        strategy.next_params(params, resp_empty)


@pytest.mark.asyncio
async def test_paginated_request_paginate():
    """测试 PaginatedRequest 的 async for 迭代流程."""

    class DummyPaginatedRequest(PaginatedRequest):
        def __await__(self):
            async def _coro():
                return DummyResponse(total=20, items=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

            return _coro().__await__()

    strategy = OffsetStrategy[Any, DummyResponse](
        offset_key="start",
        page_size_key="size",
        total_extractor=lambda r: r.total,
    )

    req = DummyPaginatedRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"start": 0, "size": 10},
        pager_strategy=strategy,
    )

    results = [res async for res in req.paginate(limit=2)]
    assert len(results) == 2


def test_refreshable_request_next_request():
    """测试 RefreshableRequest 的 next_request 方法."""
    strategy = BatchRefreshStrategy[Any, DummyResponse](
        refresh_key="vec",
        cursor_extractor=lambda r: r.next_cursor,
        has_more_extractor=lambda r: r.has_more,
    )

    req = RefreshableRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"vec": "cur1"},
        refresh_strategy=strategy,
    )

    resp_more = DummyResponse(has_more=True, next_cursor="cur2")
    next_req = req.next_request(resp_more)
    assert next_req is not None
    assert cast("dict[str, Any]", next_req.param)["vec"] == "cur2"

    resp_end = DummyResponse(has_more=False)
    assert req.next_request(resp_end) is None
