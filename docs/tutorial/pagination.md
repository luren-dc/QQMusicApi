# Pagination

QQMusicApi 提供了现代化的分页与换一批支持。

* `PaginatedRequest` 声明了连续翻页能力的请求。可以直接 `await` 发起单页请求，也可以通过 `.pager()`、`.paginate()`、`.collect()`、`.collect_items()` 或 `async for` 进行灵活消费。
* `RefreshableRequest` 声明了“换一批”能力的请求。可以通过 `.refresher()`、`.refresh_stream()`、`.collect_items()` 等手控或连续刷新拉取。

---

## 1. 单次请求与无状态步进

即使请求具备分页能力，你依然可以像普通请求一样直接 `await` 它，仅拉取单页数据：

```python
import asyncio
from qqmusic_api import Client

async def main() -> None:
    async with Client() as client:
        # 仅获取第 1 页数据
        first_page = await client.album.get_new_album(page=1, num=10)
        print(len(first_page.albums))

asyncio.run(main())
```

如果你希望配合上一次响应手动构建下一页请求：

```python
req1 = client.album.get_new_album(page=1, num=10)
res1 = await req1

# 根据上一次响应获取下一次请求的描述符
req2 = req1.next_request(res1)
if req2 is not None:
    res2 = await req2
```

---

## 2. Pager 有状态控制器（适合 Web / UI 场景）

通过 `.pager()` 可以创建一个有状态的 `AsyncPager` 控制器，包含 `has_more()` 与 `next()` 方法，极其适合 UI 的“点击下一页”交互：

```python
import asyncio
from qqmusic_api import Client

async def main() -> None:
    async with Client() as client:
        pager = client.comment.get_hot_comments(102065756, page_size=5).pager(limit=2)

        while pager.has_more():
            page = await pager.next()
            print(len(page.comments))

asyncio.run(main())
```

> `has_more()` 只读取当前分页器的内部状态，不会发起网络请求。`next()` 没有更多数据时会抛出 `StopAsyncIteration`。

---

## 3. 全量收集与条目平铺 (`collect` / `collect_items`)

如果你希望直接获取多页响应列表，或者直接获取展平后的所有实体数据项（如所有歌曲或专辑）：

```python
import asyncio
from qqmusic_api import Client

async def main() -> None:
    async with Client() as client:
        req = client.singer.get_album_list(mid="0025NhlN2yWrP4")

        # 收集前 3 页的 Response 响应对象列表
        pages = await req.collect(limit=3)
        print(f"共获取 {len(pages)} 页响应")

        # 自动跨页展开提取前 25 个专辑实体
        albums = await req.collect_items(limit=25)
        print(f"共收集 {len(albums)} 个专辑实体")

asyncio.run(main())
```

---

## 4. 异步流式迭代 (`async for`)

* **页级别迭代 (`paginate()`)**：每次迭代返回一个完整的页面响应对象。
* **条目级别迭代 (`iter_items()`)**：自动跨页提取并展平实体。

```python
import asyncio
from qqmusic_api import Client

async def main() -> None:
    async with Client() as client:
        req = client.search.search_by_type("周杰伦", num=5)

        # 方式 A：页级别迭代
        async for page in req.paginate(limit=2):
            print("当前页歌曲数:", len(page.song))

        # 方式 B：条目级别迭代
        async for song in req.iter_items(limit=10):
            print("歌曲名:", song.name)

asyncio.run(main())
```

---

## 5. Refresher 换一批用法

“换一批”接口提供 `.refresher()` 手动控制器，以及 `.refresh_stream()` 异步流式迭代器：

```python
import asyncio
from qqmusic_api import Client

async def main() -> None:
    async with Client() as client:
        # 手动控制器用法
        refresher = client.song.get_related_mv(1114857).refresher(limit=3)
        current_batch = await refresher.first()
        if refresher.has_more():
            next_batch = await refresher.next()

        # 连续换一批流式迭代
        async for batch in client.song.get_related_mv(1114857).refresh_stream(limit=2):
            print("最新批次 MV 数:", len(batch.mv))

asyncio.run(main())
```
