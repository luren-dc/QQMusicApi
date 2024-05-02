import hashlib
import json
import random
import time
from pathlib import Path

# 定义全局变量
UUID_CHARS = "0123456789ABCDEF"
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "cache"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
API_DIR = DATA_DIR / "api"

# 确保缓存目录存在
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_file(*args) -> str:
    return str(CACHE_DIR.joinpath(*args))


def get_api(field: str, *args) -> dict:
    path = API_DIR / f"{field.lower()}.json"
    if path.exists():
        with path.open(encoding="utf8") as f:
            data = json.load(f)
            for arg in args:
                data = data[arg]
            return data
    return {}


def random_string(length: int, chars: str = UUID_CHARS) -> str:
    return "".join(random.choices(chars, k=length))


def calc_md5(*multi_string) -> str:
    md5 = hashlib.md5()
    for s in multi_string:
        md5.update(s if isinstance(s, bytes) else s.encode())
    return md5.hexdigest()


def hash33(s: str, h: int = 0) -> int:
    for c in s:
        h = (h << 5) + h + ord(c)
    return 2147483647 & h


def random_uuid() -> str:
    uuid_format = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    return "".join(random.choice(UUID_CHARS) if c in "xy" else c for c in uuid_format)


def random_searchID() -> str:
    e = random.randint(1, 20)
    t = e * 18014398509481984
    n = random.randint(0, 4194304) * 4294967296
    a = time.time()
    r = round(a * 1000) % (24 * 60 * 60 * 1000)
    return str(t + n + r)


def parse_song_info(song_info: dict) -> dict:
    # 解析歌曲信息
    info = {
        "id": song_info["id"],
        "mid": song_info["mid"],
        "name": song_info["name"],
        "title": song_info["title"],
        "subTitle": song_info.get("subtitle", ""),
        "language": song_info["language"],
        "time_public": song_info.get("time_public", ""),
        "tag": song_info.get("tag", ""),
        "type": song_info["type"],
    }
    # 解析专辑信息
    album = {
        "id": song_info["album"]["id"],
        "mid": song_info["album"]["mid"],
        "name": song_info["album"]["name"],
        "time_public": song_info["album"].get("time_public", ""),
    }
    # 解析MV信息
    mv = {
        "id": song_info["mv"]["id"],
        "name": song_info["mv"].get("name", ""),
        "vid": song_info["mv"]["vid"],
    }
    # 解析歌手信息
    singer = [
        {
            "id": s["id"],
            "mid": s["mid"],
            "name": s["name"],
            "type": s.get("type"),
            "uin": s.get("uin"),
        }
        for s in song_info["singer"]
    ]
    # 解析文件信息
    file = {
        "media_mid": song_info["file"]["media_mid"],
        "new_0": song_info["file"]["size_new"][0],
        "new_1": song_info["file"]["size_new"][1],
        "new_2": song_info["file"]["size_new"][2],
        "flac": song_info["file"]["size_flac"],
        "ogg_192": song_info["file"]["size_192ogg"],
        "ogg_96": song_info["file"]["size_96ogg"],
        "mp3_320": song_info["file"]["size_320mp3"],
        "mp3_128": song_info["file"]["size_128mp3"],
        "aac_192": song_info["file"]["size_192aac"],
        "aac_96": song_info["file"]["size_96aac"],
        "aac_48": song_info["file"]["size_48aac"],
    }
    # 组装结果
    result = {
        "info": info,
        "album": album,
        "mv": mv,
        "singer": singer,
        "file": file,
        "lyric": {
            "match": song_info.get("lyric", ""),
            "content": song_info.get("content", ""),
        },
        "pay": song_info.get("pay", {}),
        "grp": [parse_song_info(song) for song in song_info.get("grp", [])],
        "vs": song_info.get("vs", []),
    }
    return result


def filter_data(data: dict) -> dict:
    keys = [""]
    for key in keys:
        data.pop(key, "")
    return data


def singer_to_str(data: dict) -> str:
    return "&".join([singer["name"] for singer in data["singer"]])
