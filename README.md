    <h1> QQMusic Api </h1>
    <p> Python QQ音乐 API 封装库 </p>

[![Python](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pdm-managed](https://img.shields.io/endpoint?url=https%3A%2F%2Fcdn.jsdelivr.net%2Fgh%2Fpdm-project%2F.github%2Fbadge.json)](https://pdm-project.org)
[![GitHub license](https://img.shields.io/github/license/luren-dc/PyQQMusicApi)](https://github.com/luren-dc/QQMusicApi/tree/build?tab=License-1-ov-file)
[![STARS](https://img.shields.io/github/stars/luren-dc/QQMusicApi?color=yellow&label=Github%20Stars)](https://github.com/luren-dc/QQMusicApi/stargazers)
[![Testing](https://github.com/luren-dc/QQMusicApi/actions/workflows/testing.yml/badge.svg?branch=dev)](https://github.com/luren-dc/QQMusicApi/actions/workflows/testing.yml)

---

> [!WARNING]
> 本仓库的所有内容仅供学习和参考之用，禁止用于商业用途。

<!----8<-- [start:intro]-->

## 介绍

使用 Python 编写的用于调用 [QQ音乐](https://y.qq.com/) 各种 API 的库.

## 特色

- 涵盖常见 API
- 调用简便，函数命名易懂，代码注释详细
- 异步操作

## 依赖

- [AIOHTTP](https://docs.aiohttp.org/)
- [Requests](https://requests.readthedocs.io/)
- [Cryptography](https://cryptography.io/)
<!----8<-- [end:intro]-->

## 帮助

查看[文档](https://luren-dc.github.io/QQMusicApi/)更多帮助

## 快速上手

### 安装

```bash
$ pip install qqmusic-api-python
```

### 使用

<!----8<-- [start:example]-->

```python exec="1" result="pycon" source="tabbed-left"
import asyncio

from qqmusic_api import search

async def main():
    # 搜索歌曲
    result = await search.search_by_type(keyword="周杰伦", num=20)
    # 打印结果
    print(result)

asyncio.run(main())
```

<!----8<-- [end:example]-->

<!----8<-- [start:refer]-->

## 参考项目

- [Rain120/qq-muisc-api](https://github.com/Rain120/qq-music-api)
- [jsososo/QQMusicApi](https://github.com/jsososo/QQMusicApi)
- [Nemo2011/bilibili-api](https://github.com/Nemo2011/bilibili-api/)
<!----8<-- [end:refer]-->

## Licence

**[MIT License](https://github.com/luren-dc/QQMusicApi?tab=MIT-1-ov-file)**
