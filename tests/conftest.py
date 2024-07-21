import os

import pytest

from qqmusic_api import Credential
from qqmusic_api.album import Album
from qqmusic_api.mv import MV
from qqmusic_api.singer import Singer
from qqmusic_api.song import Song
from qqmusic_api.songlist import Songlist
from qqmusic_api.top import Top


@pytest.fixture(scope="package")
def credential():
    musicid = str(os.getenv("MUSIC_ID"))
    musickey = str(os.getenv("MUSIC_KEY"))
    refresh_key = str(os.getenv("MUSIC_REFRESH_KEY"))
    return Credential(musicid=musicid, musickey=musickey, refresh_key=refresh_key)


@pytest.fixture(scope="package")
def album():
    return Album("000MkMni19ClKG")


@pytest.fixture(scope="package")
def mv():
    return MV("003HjRs318mRL2")


@pytest.fixture(scope="package")
def singer():
    return Singer("0025NhlN2yWrP4")


@pytest.fixture(scope="package")
def song():
    return Song(mid="004emQMs09Z1lz")


@pytest.fixture(scope="package")
def songlist():
    return Songlist(9069454203)


@pytest.fixture(scope="package")
def top():
    return Top(62)
