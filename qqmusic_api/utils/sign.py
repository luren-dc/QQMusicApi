"""QQ音乐 sign"""

import base64
import json

from .common import calc_md5


def _head(b: bytes) -> list:
    p = [21, 4, 9, 26, 16, 20, 27, 30]
    return [b[x] for x in p]


def _tail(b: bytes) -> list:
    p = [18, 11, 3, 2, 1, 7, 6, 25]
    return [b[x] for x in p]


def _middle(b: bytes) -> list:
    zd = {
        "0": 0,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "A": 10,
        "B": 11,
        "C": 12,
        "D": 13,
        "E": 14,
        "F": 15,
    }
    ol = [212, 45, 80, 68, 195, 163, 163, 203, 157, 220, 254, 91, 204, 79, 104, 6]
    res = []
    j = 0
    for i in range(0, len(b), 2):
        one = zd[chr(b[i])]
        two = zd[chr(b[i + 1])]
        r = one * 16 ^ two
        res.append(r ^ ol[j])
        j += 1
    return res


def sign(request: dict) -> str:
    """QQ音乐 请求签名

    Args:
        request: 请求数据

    Returns:
        签名结果
    """
    md5_str = calc_md5(json.dumps(request, ensure_ascii=False, separators=(",", ":"))).upper().encode("utf-8")

    h = _head(md5_str)
    e = _tail(md5_str)
    ls = _middle(md5_str)
    m = base64.b64encode(bytes(ls)).decode("utf-8")

    res = "zzb" + "".join(map(chr, h)) + m + "".join(map(chr, e))
    return res.lower().replace("/", "").replace("+", "").replace("=", "")
