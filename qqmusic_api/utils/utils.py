"""实用函数"""

import json
import os
import random
import time
from typing import Union
from zlib import decompress

from .tripledes import DECRYPT, tripledes_crypt, tripledes_key_setup


def get_api(field: str) -> dict:
    """获取 api 字典

    Args:
        field: 字段名

    Returns:
        api 字典
    """
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "api", f"{field.lower()}.json"))
    if os.path.exists(path):
        with open(path, encoding="utf8") as f:
            data = json.load(f)
            return data
    else:
        return {}


def get_guid() -> str:
    """随机 guid

    Returns:
        随机 guid
    """
    return "".join(random.choices("abcdef1234567890", k=32))


def hash33(s: str, h: int = 0) -> int:
    """hash33

    Args:
        s: 待计算的字符串
        h: 前一个计算结果
    Returns:
        计算结果
    """
    for c in s:
        h = (h << 5) + h + ord(c)
    return 2147483647 & h


def get_searchID() -> str:
    """随机 searchID

    Returns:
        随机 searchID
    """
    e = random.randint(1, 20)
    t = e * 18014398509481984
    n = random.randint(0, 4194304) * 4294967296
    a = time.time()
    r = round(a * 1000) % (24 * 60 * 60 * 1000)
    return str(t + n + r)


def qrc_decrypt(encrypted_qrc: Union[str, bytearray, bytes]) -> str:
    """QRC 解码

    Args:
        encrypted_qrc: 加密的 QRC 数据

    Returns:
        解密后的 QRC 数据

    Raises:
        ValueError: 解密失败
    """
    if not encrypted_qrc:
        return ""

    # 将输入转为 bytearray 格式
    if isinstance(encrypted_qrc, str):
        encrypted_qrc = bytearray.fromhex(encrypted_qrc)
    elif isinstance(encrypted_qrc, (bytearray, bytes)):
        encrypted_qrc = bytearray(encrypted_qrc)
    else:
        raise ValueError("无效的加密数据类型")

    try:
        data = bytearray()
        schedule = tripledes_key_setup(b"!@#)(*$%123ZXC!@!@#)(NHL", DECRYPT)

        # 分块解密数据
        # 以 8 字节为单位迭代 encrypted_qrc
        for i in range(0, len(encrypted_qrc), 8):
            data += tripledes_crypt(encrypted_qrc[i:], schedule)

        decrypted_qrc = decompress(data).decode("utf-8")
        return decrypted_qrc

    except Exception as e:
        raise ValueError(f"解密失败: {e}")
