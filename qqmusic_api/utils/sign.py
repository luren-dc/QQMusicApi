"""QQ音乐 sign"""

import re
from base64 import b64encode
from hashlib import sha1

import orjson as json

PART_1_INDEXES = [23, 14, 6, 36, 16, 40, 7, 19]
PART_2_INDEXES = [16, 1, 32, 12, 19, 27, 8, 5]
SCRAMBLE_VALUES = [89, 39, 179, 150, 218, 82, 58, 252, 177, 52, 186, 123, 120, 64, 242, 133, 143, 161, 121, 179]

# JavaScript quirks emulation
PART_1_INDEXES = filter(lambda x: x < 40, PART_1_INDEXES)


def sign(request: dict) -> str:
    """QQ音乐 请求签名

    Args:
        request: 请求数据

    Returns:
        签名结果
    """
    hash = sha1(json.dumps(request)).hexdigest().upper()

    part1 = "".join(hash[i] for i in PART_1_INDEXES)
    part2 = "".join(hash[i] for i in PART_2_INDEXES)

    part3 = bytearray(20)
    for i, v in enumerate(SCRAMBLE_VALUES):
        value = v ^ int(hash[i * 2 : i * 2 + 2], 16)
        part3[i] = value
    b64_part = re.sub(rb"[\\/+=]", b"", b64encode(part3)).decode("utf-8")
    return f"zzc{part1}{b64_part}{part2}".lower()
