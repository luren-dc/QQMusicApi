# 执行异步代码

> [!NOTE]
> 代码来源： [bilibili-api](https://github.com/Nemo2011/bilibili-api)

方便的异步转同步，使用方法如下：

```python
from qqmusic_api import sync
from qqmusic_api.mv import MV

mv = MV("i0043gp575k")
sync(mv.get_url())
```

实现原理如下：

```python
--8<-- "qqmusic_api/utils/sync.py"
```
