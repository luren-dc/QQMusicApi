from .login import Login, LoginApi
from .search import SearchApi
from .song import SongApi
from .top import TopApi


def set_parent(parent):
    Login.parent = parent
    LoginApi.parent = parent
    SearchApi.parent = parent
    SongApi.parent = parent
    TopApi.parent = parent
