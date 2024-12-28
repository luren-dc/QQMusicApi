# Session

实现 QQ音乐 API请求管理，支持设置全局 `Credential`

## 示例

```python
from qqmusic_api import create_session, get_session, set_session


async def main():
    # 获取当前 EventLoop 的 Session
    get_session()
    # 设置当前 EventLoop 的 Session
    set_session(create_session())
    async with create_session():
        # 进入该 Session, 在 `async with` 内的 API 将由该 Session 完成
        ...
        # 离开 Session. 此后 API 将继续由全局 Session 管理
```
