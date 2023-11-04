from .login import Login, LoginApi
from .mv import MvApi
from .playlist import PlaylistApi
from .search import SearchApi
from .song import SongApi
from .top import TopApi


def set_parent(parent):
    Login.parent = parent
    LoginApi.parent = parent
    SearchApi.parent = parent
    SongApi.parent = parent
    TopApi.parent = parent
    MvApi.parent = parent
    PlaylistApi.parent = parent
