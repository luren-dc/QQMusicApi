from . import album, login, mv, search, singer, song, songlist, top
from .utils.credential import Credential
from .utils.network import get_aiohttp_session, set_aiohttp_session

__version__ = "0.1.2"

__all__ = [
    "album",
    "Credential",
    "get_aiohttp_session",
    "login",
    "mv",
    "search",
    "set_aiohttp_session",
    "singer",
    "song",
    "songlist",
    "top",
]
