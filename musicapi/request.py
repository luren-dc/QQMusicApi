import requests

from .exceptions import RequestException


class Request:
    HEADER = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/81.0.4044.129 Safari/537.36,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
        "Referer": "https://y.qq.com/",
    }

    @classmethod
    def get(cls, headers: dict = {}, **kwargs):
        """
        发送 GET 请求

        :param kwargs: 请求参数
        :return:
        """
        headers = headers if headers else cls.HEADER
        try:
            requests.get(headers=headers, **kwargs)
        except Exception as e:
            raise RequestException(e.__str__())

    @classmethod
    def post(cls, headers: dict = {}, **kwargs):
        """
        发送 POST 请求

        :param kwargs: 请求参数
        :return:
        """
        headers = headers if headers else cls.HEADER
        try:
            requests.postj(headers=headers, **kwargs)
        except Exception as e:
            raise RequestException(e.__str__())
