import hashlib
import random
import time
from typing import Any, Dict, List


def random_string(length: int, chars: str) -> str:
    return "".join(random.choices(chars, k=length))


def calc_md5(*multi_string) -> str:
    md5 = hashlib.md5()
    for s in multi_string:
        md5.update(s if isinstance(s, bytes) else s.encode())
    return md5.hexdigest()


def get_ptqrtoken(qrsig: str) -> int:
    e = 0
    for c in qrsig:
        e += (e << 5) + ord(c)
    return 2147483647 & e


def get_token(p_skey: str) -> int:
    h = 5381
    for c in p_skey:
        h += (h << 5) + ord(c)
    return 2147483647 & h


def random_uuid() -> str:
    uuid_string = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"

    def callback(c: str) -> str:
        r = random.randint(0, 15)
        v = r if c == "x" else (r & 0x3 | 0x8)
        return hex(v)[2:]

    return "".join([callback(c) if c in ["x", "y"] else c for c in uuid_string]).upper()


def random_searchID() -> str:
    e = random.randint(1, 20)
    t = e * 18014398509481984
    n = random.randint(0, 4194304) * 4294967296
    a = time.time()
    r = round(a * 1000) % (24 * 60 * 60 * 1000)
    return str(t + n + r)


def ensure_list(value: Any) -> List:
    if isinstance(value, list):
        return value
    else:
        return [value] if value else []


def parse_song_info(song_info: Dict) -> Dict:
    # 解析歌曲信息
    info = {
        "id": song_info["id"],
        "mid": song_info["mid"],
        "name": song_info["name"],
        "title": song_info["title"],
        "subTitle": song_info.get("subtitle", ""),
        "language": song_info["language"],
        "timePublic": song_info.get("time_public", ""),
        "tag": song_info.get("tag", ""),
        "type": song_info["type"],
    }

    # 解析专辑信息
    album = {
        "id": song_info["album"]["id"],
        "mid": song_info["album"]["mid"],
        "name": song_info["album"]["name"],
        "timePublic": song_info["album"].get("time_public", ""),
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
        "mediaMid": song_info["file"]["media_mid"],
        "AI00": song_info["file"]["size_new"][0],
        "Q000": song_info["file"]["size_new"][1],
        "Q001": song_info["file"]["size_new"][2],
        "F000": song_info["file"]["size_flac"],
        "O600": song_info["file"]["size_192ogg"],
        "O400": song_info["file"]["size_96ogg"],
        "M800": song_info["file"]["size_320mp3"],
        "M500": song_info["file"]["size_128mp3"],
        "C600": song_info["file"]["size_192aac"],
        "C400": song_info["file"]["size_96aac"],
        "C200": song_info["file"]["size_48aac"],
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


def filter_data(data: Dict) -> Dict:
    keys = [
        "relainfo",
        "identity",
        "iconurl",
        "page_rank",
        "settleIn",
        "is_intervene",
        "isFollow",
        "pic_icon",
        "hotness",
        "audio_play",
        "hotness_desc",
        "smallIcons",
        "pay",
        "notplay",
        "new_video_switch",
        "msg",
        "mid_desc",
        "auto_play",
        "watchtype",
        "watchid",
        "video_switch",
        "video_pay",
        "pmid",
        "track_id",
    ]
    for key in keys:
        data.pop(key, "")
    return data


def singer_to_str(data: Dict):
    return "&".join([singer["name"] for singer in data["singer"]])


def split_list(lst: List, chunk_size: int) -> List:
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def search_song(songs: List[Dict], mid: str) -> Dict:
    return next(filter(lambda x: x["info"]["mid"] == mid, songs), {})
