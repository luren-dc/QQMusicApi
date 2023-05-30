import time
from typing import Any

import requests

from .exceptions import RequestException
from .utils import Utils


class Request:
    HEADER = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/81.0.4044.129 Safari/537.36,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
        "Referer": "https://y.qq.com/",
    }

    @classmethod
    def get(cls, url: str, headers: dict = {}, params: dict = {}) -> dict[str, Any]:
        """
        发送 GET 请求

        :param url: 请求链接
        :param headers: 请求头
        :param params：请求参数
        :return: 请求结果
        """
        headers = headers if headers else cls.HEADER
        try:
            response = requests.get(url, headers=headers, params=params)
            return response.json()
        except Exception as e:
            raise RequestException(e.__str__())

    @classmethod
    def post(
        cls,
        url: str,
        headers: dict = {},
        params: dict = {},
        data: dict = {},
        needsign: bool = True,
    ) -> dict[str, Any]:
        """
        发送 POST 请求
        :param url: 请求链接
        :param headers: 请求头
        :param data: 请求体
        :param params：请求参数
        :param needsign: 是否需要sign
        :return: 请求结果
        """
        headers = headers if headers else cls.HEADER
        str_data = Utils.format_data(data)
        if needsign:
            params["_"] = str(int(time.time() * 1000))
            params["sign"] = Utils.get_sign(str_data)
        try:
            response = requests.post(
                url, headers=headers, params=params, data=str_data.encode("utf-8")
            )
            return response.json()
        except Exception as e:
            raise RequestException(e.__str__())
