# Logging

如果您需要检查 `QQMusicApi` 的内部行为，您可以使用 Python 的 `logging` 来输出有关底层网络行为的信息。

例如，以下配置...

```python
import logging

from qqmusic_api import sync
from qqmusic_api.search import general_search

logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

sync(general_search("周杰伦"))
```
会将调试级别输出发送到控制台，或者发送到 `stdout`...

```shell
DEBUG [2024-12-22 06:24:56] qqmusicapi - 获取 QIMEI 成功: {'code': 0, 'msg': 'success', 'data': '{"code":0,"msg":"ok","data":{"q16":"fde9508748b00283b2723a9210001b617301","q36":"0a58b2118fe71bf0ab567d56100018c1730d"}}', 'timestamp': 1734848695}
DEBUG [2024-12-22 06:24:56] qqmusicapi - 发起请求: https://u.y.qq.com/cgi-bin/musicu.fcg music.adaptor.SearchAdaptor do_search_v2 music.adaptor.SearchAdaptor params: {} data: {'comm': {'ct': '11', 'cv': 13020508, 'v': 13020508, 'tmeAppID': 'qqmusic', 'QIMEI36': '0a58b2118fe71bf0ab567d56100018c1730d', 'uid': '3931641530', 'format': 'json', 'inCharset': 'utf-8', 'outCharset': 'utf-8'}, 'request': {'module': 'music.adaptor.SearchAdaptor', 'method': 'do_search_v2', 'param': {'searchid': '295717586503494319', 'search_type': 100, 'query': '周杰伦', 'grp': 1, 'highlight': 1, 'page_id': 1, 'page_num': 15}}}
DEBUG [2024-12-22 06:24:57] qqmusicapi - API music.adaptor.SearchAdaptor.do_search_v2: 0
```
