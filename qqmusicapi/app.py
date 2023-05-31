from flask import Flask

from qqmusicapi.api.search import Search

app = Flask(__name__)


@app.route("/")
def index():
    return "<p>Hello, World!</p>"


@app.route("/search/<search_type>")
def search(search_type: str = "song"):
    return Search.search("xiaochou", search_type=search_type, page=1)


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
