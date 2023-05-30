from flask import Flask
from qqmusicapi.api.search import Search

app = Flask(__name__)


@app.route("/")
def index():
    return "<p>Hello, World!</p>"


@app.route("/search")
def search():
    return Search.search("陈奕迅", search_type="song", page=1, num=10)

def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
