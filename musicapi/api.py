import json
from abc import ABC, abstractmethod
from typing import Any
from requests import post, get


class Api(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def search(self, query, search_type, num, page):
        pass

    @abstractmethod
    def get_song_list(self, songlist_id):
        pass


class QQMusic(Api):
    # 不需要 sign
    _API_URL = "https://u.y.qq.com/cgi-bin/musicu.fcg"
    # 需要 sign
    _ENCRYPT_API_URL = "https://u.y.qq.com/cgi-bin/musics.fcg"

    def __init__(self) -> None:
        super().__init__()
        self.encrypt_api = 1
        self.qqmusic_skey = ""
