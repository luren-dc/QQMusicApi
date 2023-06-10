from flask import Flask, request
from flask_caching import Cache

from qqmusicapi.api.search import Search
from qqmusicapi.api.song import Song
from qqmusicapi.api.songlist import SongList

app = Flask(__name__)
cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "../.cache",
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
    query = request.args.get("query", None)
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
        only_song = int(request.args.get("only_song", 0))
    except ValueError:
        only_song = 0
    try:
        creator_info = int(request.args.get("creator_info", 1))
    except ValueError:
        creator_info = 1
    return SongList.get_detail(int(songlist_id), only_song, creator_info)


@app.route("/song/urls")
@cache.cached(query_string=True)
def get_urls():
    mid = request.args.get("mid", [])
    mid = mid.split(",")
    file_type = request.args.get("filetype", "128")
    return Song.url(mid, file_type)


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
