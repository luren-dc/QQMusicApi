import logging

from . import album, comment, login, lyric, mv, search, singer, song, songlist, top, user
from .utils.credential import Credential
from .utils.session import Session, get_session, set_session

__version__ = "0.3.6"

logger = logging.getLogger("qqmusicapi")


__all__ = [
    "Credential",
    "Session",
    "album",
    "comment",
    "get_session",
    "login",
    "lyric",
    "mv",
    "search",
    "set_session",
    "singer",
    "song",
    "songlist",
    "top",
    "user",
]
