import logging

from . import album, login, login_utils, lyric, mv, search, singer, song, songlist, top, user
from .utils.credential import Credential
from .utils.network import get_session, set_session
from .utils.sync import sync

__version__ = "0.1.11"

logger = logging.getLogger("qqmusicapi")


__all__ = [
    "album",
    "Credential",
    "get_session",
    "login",
    "login_utils",
    "lyric",
    "mv",
    "search",
    "set_session",
    "singer",
    "song",
    "songlist",
    "sync",
    "top",
    "user",
]
