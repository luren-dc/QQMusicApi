<div align="center">
    <h1> PyQQMusicApi </h1>
    <p> Python QQ音乐Api封装库 </p>

![Python Version 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub license](https://img.shields.io/github/license/luren-dc/QQMusicApi)](https://github.com/luren-dc/QQMusicApi/blob/master/LICENSE)

</div>

---

> [!NOTE]
> 编程技术有待提高，架构有待优化

## 🎊介绍

**调用QQ音乐接口，获取相关数据**

> [!WARNING]
> 本项目仅供学习使用，请尊重版权，请勿利用此项目从事商业行为!

> [!NOTE]
> 获取高品质音乐播放链接需要豪华绿钻或超级会员

本项目基于：

- [AIOHTTP](https://docs.aiohttp.org/)
- [Requests](https://requests.readthedocs.io/)
- [Cryptography](https://cryptography.io/)

## ✨功能

- 歌曲接口
- 登录接口
- MV接口
- 歌单接口
- 排行榜接口
- 搜索接口
- 专辑接口

## 💡安装
```shell
pip install git+https://github.com/luren-dc/PyQQMusicApi.git
```

## 🔥使用

```python
import asyncio
from pyqqmusicapi import QQMusic

# 初始化Api，可传入musicid，musickey
api = QQMusic()

# 后续更新token
api.update_token(musicid,musickey)

# 可用api：SongApi，TopApi，SearchApi，MvApi，PlaylistApi，AlbumApi，LoginApi

# 搜索示例
asyncio.run(api.search.query("周杰伦"))
```

**更多请查看[测试用例](https://github.com/luren-dc/PyQQMusicApi/tree/dev/tests)**

## 🗒️TODO

- [ ] WEB端接口
- [ ] 使用示例
- [ ] 更多接口
- [ ] 日志功能

## Licence

**[MIT License](https://github.com/luren-dc/QQMusicApi/blob/master/LICENSE)**
