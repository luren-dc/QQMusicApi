# Session

实现 QQ音乐 API请求管理，每个 `EventLoop` 对应一个全局 `Session`,可以创建使用多个 `Session`

## 使用加密接口

```python
from qqmusic_api import Session

async def main():
  async with Session(enable_sign=True):
      ...
```

## 设置 Credential

```python
from qqmusic_api import Session, Credential, get_session

async def main():
  # 设置全局 Credential
  get_session().credential = Credential()

  async with Session(enable_sign=True,credential=Credential()):
      ...
```

## 示例

```python
from qqmusic_api import get_session, set_session


async def main():
    # 获取当前 EventLoop 的 Session
    get_session()

    # 设置当前 EventLoop 的 Session
    set_session(Session())

    # 新建 Session
    async with Session():
        # 进入该 Session, 在 `async with` 内的 API 将由该 Session 完成
        ...
        # 离开 Session. 此后 API 将继续由全局 Session 管理
```
