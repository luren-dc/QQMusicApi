import logging

from . import album, login, login_utils, lyric, mv, search, singer, song, songlist, top, user
from .utils.credential import Credential
from .utils.session import create_session, get_session, set_session, set_session_credential
from .utils.sync import sync

__version__ = "0.2.0"

logger = logging.getLogger("qqmusicapi")


__all__ = [
    "Credential",
    "album",
    "create_session",
    "get_session",
    "login",
    "login_utils",
    "lyric",
    "mv",
    "search",
    "set_session",
    "set_session_credential",
    "singer",
    "song",
    "songlist",
    "sync",
    "top",
    "user",
]
