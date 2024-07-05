<div align="center">
    <h1> QQMusicApi </h1>
    <p> Python QQ音乐 API 封装库 </p>

![Python Version 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![GitHub license](https://img.shields.io/github/license/luren-dc/PyQQMusicApi)

</div>

---

> [!WARNING]
> 本仓库的所有内容仅供学习和参考之用，禁止用于商业用途。

## 介绍

使用 Python 编写的用于调用 [QQ音乐](https://y.qq.com/) 各种 API 的库.

## 依赖

本项目基于：

- [AIOHTTP](https://docs.aiohttp.org/)
- [Requests](https://requests.readthedocs.io/)
- [Cryptography](https://cryptography.io/)

## 快速上手

### 安装

```shell
$ pip install qqmusic-api-python
```

### 使用

```python
import asyncio

from qqmusic_api import search

async def main():
    # 搜索歌曲
    result = await search.search_by_type(keyword="周杰伦", num=20)
    # 打印结果
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## TODO

- [ ] 歌手 API
- [ ] 评论 API
- [ ] 用户 API

## 参考项目

- [Rain120/qq-muisc-api](https://github.com/Rain120/qq-music-api)
- [jsososo/QQMusicApi](https://github.com/jsososo/QQMusicApi)
- [Nemo2011/bilibili-api](https://github.com/Nemo2011/bilibili-api/)

## Licence

**[MIT License](https://github.com/luren-dc/QQMusicApi/blob/master/LICENSE)**
