import time

from flask import Flask, request, send_file
from flask_caching import Cache

from qqmusicapi.api.login import Login
from qqmusicapi.api.search import Search
from qqmusicapi.api.song import Song
from qqmusicapi.api.songlist import SongList
from qqmusicapi.exceptions import ParamsException

app = Flask(__name__)
cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": ".cache",
        "CACHE_DEFAULT_TIMEOUT": 300,
    }
)
cache.init_app(app)


@app.route("/")
def index():
    return "<p>Hello, World!</p>"


@app.route("/search/<search_type>", methods=["GET"])
@cache.cached(query_string=True)
def search(search_type: str):
    query = request.args.get("query", "")
    try:
        num = int(request.args.get("num", 10))
    except ValueError:
        num = 10
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    return Search.search(query, search_type=search_type, page=page, num=num)


@app.route("/quicksearch/<query>")
@cache.cached(query_string=True)
def quicksearch(query: str):
    return Search.quick_search(query)


@app.route("/songlist/<songlist_id>", methods=["GET"])
@cache.cached(query_string=True)
def songlist(songlist_id: int):
    try:
        only_song = int(request.args.get("onlySong", 0))
    except ValueError:
        only_song = 0
    try:
        creator_info = int(request.args.get("creatorInfo", 1))
    except ValueError:
        creator_info = 1
    return SongList.get_detail(int(songlist_id), only_song, creator_info)


@app.route("/song/urls", methods=["GET"])
@cache.cached(query_string=True)
def get_urls():
    mid = request.args.get("mid", "")
    mid = mid.split(",")
    file_type = request.args.get("filetype", "128")
    return Song.url(mid, file_type)


@app.route("/login/<login_type>", methods=["GET"])
def login(login_type: str):
    if login_type == "get_login_id":
        lg = Login()
        login_id = lg.get_login_id()
        while cache.get(login_id):
            login_id = lg.get_login_id()
        cache.set(login_id, lg)
        cache.set(login_id + "time", time.time())
        return {"code": 200, "data": {"loginID": login_id}}
    else:
        login_id = request.args.get("loginID", "")
        if not login_id:
            raise ParamsException("缺少 loginID")
        lg = cache.get(login_id)
        id_time = cache.get(login_id + "time")
        id_time = id_time if id_time else 0
        if (not lg) or (time.time() - id_time) > 400:
            print(time.time() - id_time)
            raise ParamsException("loginID 无效")
        if login_type == "get_qrcode":
            data = send_file(lg.get_qrcode(), mimetype="image/png")
        else:
            data = lg.login(login_type)
        cache.set(login_id, lg)
        return data


def main():
    app.run(debug=True, host="0.0.0.0")


if __name__ == "__main__":
    main()
