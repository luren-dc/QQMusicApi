import hashlib
import json
import random
import time
from random import randint


class Utils:
    @staticmethod
    def format_data(data: dict) -> str:
        """
        格式化请求数据
        :param data: 请求数据
        :return: 格式化结果
        """
        f_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        return f_data

    @staticmethod
    def get_token(p_skey: str) -> int:
        """
        计算 g_tk
        :param p_skey: 签名
        :return: g_tk
        """
        h = 5381
        if p_skey:
            for c in p_skey:
                h += (h << 5) + ord(c)
            return 2147483647 & h
        else:
            return h

    @staticmethod
    def get_sign(data: str) -> str:
        """
        计算 QQ音乐 sign
        :param data: 加密数据
        :return:
        """
        k1 = {
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
        l1 = [
            212,
            45,
            80,
            68,
            195,
            163,
            163,
            203,
            157,
            220,
            254,
            91,
            204,
            79,
            104,
            6,
        ]
        t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        md5 = hashlib.md5(data.encode()).hexdigest().upper()
        t1 = "".join([md5[i] for i in [21, 4, 9, 26, 16, 20, 27, 30]])
        t3 = "".join([md5[i] for i in [18, 11, 3, 2, 1, 7, 6, 25]])
        ls2 = []
        for i in range(16):
            x1 = k1[md5[i * 2]]
            x2 = k1[md5[i * 2 + 1]]
            x3 = ((x1 * 16) ^ x2) ^ l1[i]
            ls2.append(x3)
        ls3 = []
        for i in range(6):
            if i == 5:
                ls3.append(t[ls2[-1] >> 2])
                ls3.append(t[(ls2[-1] & 3) << 4])
            else:
                x4 = ls2[i * 3] >> 2
                x5 = (ls2[i * 3 + 1] >> 4) ^ ((ls2[i * 3] & 3) << 4)
                x6 = (ls2[i * 3 + 2] >> 6) ^ ((ls2[i * 3 + 1] & 15) << 2)
                x7 = 63 & ls2[i * 3 + 2]
                ls3.extend(t[x4] + t[x5] + t[x6] + t[x7])
        t2 = "".join(ls3)
        for s in "[\\/+=]":
            if s in t2:
                t2 = t2.replace(s, "")
        sign = f"zzb{(t1 + t2 + t3).lower()}"
        return sign

    @staticmethod
    def get_search_id(search_type: str) -> str:
        """
        计算 QQ音乐 search_id

        :param search_type:  搜索类型
        :return:
        """
        all_type = {
            "song": 3,
            "album": 4,
            "playlist": 6,
            "singer": 8,
            "user": 13,
            "lyric": 5,
            "mv": 7,
        }
        e = all_type[search_type]
        t = e * 18014398509481984
        n = randint(0, 4194304) * 4294967296
        a = time.time()
        r = round(a * 1000) % (24 * 60 * 60 * 1000)
        return str(t + n + r)

    @staticmethod
    def get_guid() -> str:
        """
        生成 guid
        :return: guid
        """
        a = int(time.time() * 1000 % 1000)
        guid = str((random.randint(0, 2147483647) * a) % 10000000000)
        return guid

    @staticmethod
    def get_uuid() -> str:
        """
        生成随机 UUID.
        :return: UUID
        """
        uuid_string = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"

        def callback(c):
            r = random.randint(0, 15)
            v = r if c == "x" else (r & 0x3 | 0x8)
            return hex(v)[2:]

        return "".join(
            [callback(c) if c in ["x", "y"] else c for c in uuid_string]
        ).upper()

    @staticmethod
    def get_ptqrtoken(qrsig: str) -> int:
        """
        计算 ptqrtoken

        :param qrsig: 签名
        :return: ptqrtoken
        """
        e = 0
        for c in qrsig:
            e += (e << 5) + ord(c)
        return 2147483647 & e
