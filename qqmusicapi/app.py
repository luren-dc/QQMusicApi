from flask import Flask

from qqmusicapi.api.search import Search
from flask import request

from qqmusicapi.api.songlist import SongList

app = Flask(__name__)


@app.route("/")
def index():
    return "<p>Hello, World!</p>"


@app.route("/search/<search_type>", methods=["GET"])
def search(search_type: str):
    query = request.args.get("query", "")
    try:
        num = int(request.args.get("num", 1))
    except ValueError:
        num = 10
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    return Search.search(query, search_type=search_type, page=page, num=num)


@app.route("/quicksearch/<query>")
def quicksearch(query: str):
    return Search.quick_search(query)


@app.route("/songlist/<songlist_id>", methods=["GET"])
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


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
