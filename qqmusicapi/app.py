from flask import Flask

from qqmusicapi.api.search import Search
from flask import request

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


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
