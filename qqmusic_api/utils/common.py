"""实用函数"""

import hashlib
import json
import os
import random
import time
import zlib
from typing import Union

from .tripledes import DECRYPT, tripledes_crypt, tripledes_key_setup


def calc_md5(*strings: Union[str, bytes]) -> str:
    """计算 MD5 值"""
    md5 = hashlib.md5()
    for item in strings:
        if isinstance(item, bytes):
            md5.update(item)
        elif isinstance(item, str):
            md5.update(item.encode())
        else:
            raise ValueError(f"Unsupported type: {type(item)}")
    return md5.hexdigest()


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
            return json.load(f)
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
            data += tripledes_crypt(encrypted_qrc[i : i + 8], schedule)

        return zlib.decompress(data).decode("utf-8")

    except Exception as e:
        raise ValueError(f"解密失败: {e}")
