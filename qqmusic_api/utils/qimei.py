import base64
import datetime
import hashlib
import json
import random
import time
from dataclasses import dataclass

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDEIxgwoutfwoJxcGQeedgP7FG9qaIuS0qzfR8gWkrkTZKM2iWHn2ajQpBRZjMSoSf6+KJGvar2ORhBfpDXyVtZCKpqLQ+FLkpncClKVIrBwv6PHyUvuCb0rIarmgDnzkfQAqVufEtR64iazGDKatvJ9y6B9NMbHddGSAUmRTCrHQIDAQAB
-----END PUBLIC KEY-----"""
SECRET = "ZdJqM15EeO2zWc08"
APP_KEY = "0AND0HD6FE4HY80F"


@dataclass
class QImeiResult:
    q16: str
    q36: str


def calculate_md5(*strings: str | bytes) -> str:
    md5 = hashlib.md5()
    for item in strings:
        if isinstance(item, bytes):
            md5.update(item)
        elif isinstance(item, str):
            md5.update(item.encode())
        else:
            raise ValueError(f"Unsupported type: {type(item)}")
    return md5.hexdigest()


def calculate_luhn_checksum(number_str: str) -> int:
    def digits_of(n: int) -> list[int]:
        return [int(digit) for digit in str(n)]

    digits = digits_of(int(number_str))
    odd_digits_sum = sum(digits[-1::-2])
    even_digits_sum = sum([sum(digits_of(2 * digit)) for digit in digits[-2::-2]])
    total_sum = odd_digits_sum + even_digits_sum
    return (10 - total_sum % 10) % 10


def rsa_encrypt(content: bytes) -> bytes:
    key = serialization.load_pem_public_key(PUBLIC_KEY.encode())
    return key.encrypt(content, padding.PKCS1v15())  # type: ignore


class AES:
    block_size = 16

    def __init__(self, key: bytes):
        self._cipher = Cipher(algorithms.AES(key), modes.CBC(key))

    @staticmethod
    def _pad(v: bytes) -> bytes:
        padding_size = AES.block_size - len(v) % AES.block_size
        return v + (padding_size * chr(padding_size)).encode()

    @staticmethod
    def _unpad(v: bytes) -> bytes:
        return v[: -v[-1]]

    def encrypt(self, content: bytes) -> bytes:
        enc = self._cipher.encryptor()
        return enc.update(self._pad(content)) + enc.finalize()

    def decrypt(self, content: bytes) -> bytes:
        dec = self._cipher.decryptor()
        return self._unpad(dec.update(content) + dec.finalize())


class DeviceData:
    """生成设备相关数据"""

    @staticmethod
    def generate_random_payload(app_version: str) -> dict:
        beacon_id = DeviceData.generate_beacon_id()
        brand = random.choice(("VIVO", "Xiaomi", "OPPO", "HUAWEI", "Redmi", "Realme"))
        fixed_rand_seconds = random.randint(0, 14400)
        current_time = datetime.datetime.now()
        time_result = current_time - datetime.timedelta(seconds=fixed_rand_seconds)
        formatted_time = time_result.strftime("%Y-%m-%d %H:%M:%S")

        reserved = {
            "harmony": "0",
            "clone": "0",
            "containe": "",
            "oz": "UhYmelwouA+V2nPWbOvLTgN2/m8jwGB+yUB5v9tysQg=",
            "oo": "Xecjt+9S1+f8Pz2VLSxgpw==",
            "kelong": "0",
            "uptimes": formatted_time,
            "multiUser": "0",
            "bod": brand,
            "brd": brand,
            "dv": "PCRT00",
            "firstLevel": "",
            "manufact": brand,
            "name": "PCRT00",
            "host": "se.infra",
            "kernel": "Linux localhost 5.10.123-android+ #1000 SMP Sun Jul 14 15:40:18 CST 2024 armv8",
        }

        return {
            "androidId": "BRAND.141613.779",
            "platformId": 1,
            "appKey": APP_KEY,
            "appVersion": app_version,
            "beaconIdSrc": beacon_id,
            "brand": brand,
            "channelId": "10003505",
            "cid": "",
            "imei": DeviceData.generate_random_imei(),
            "imsi": "",
            "mac": "",
            "model": "",
            "networkType": "unknown",
            "oaid": "",
            "osVersion": "Android 13.0,level 33",
            "qimei": "",
            "qimei36": "",
            "sdkVersion": "1.2.13.6",
            "targetSdkVersion": "33",
            "audit": "",
            "userId": "{}",
            "packageId": "com.tencent.qqmusic",
            "deviceType": "Phone",
            "sdkName": "",
            "reserved": json.dumps(reserved, separators=(",", ":"), ensure_ascii=False),
        }

    @staticmethod
    def generate_beacon_id() -> str:
        beacon_id = ""
        time_month = datetime.datetime.now().strftime("%Y-%m-") + "01"
        rand1 = random.randint(100000, 999999)
        rand2 = random.randint(100000000, 999999999)

        for i in range(1, 41):
            if i in [1, 2, 13, 14, 17, 18, 21, 22, 25, 26, 29, 30, 33, 34, 37, 38]:
                beacon_id += f"k{i}:{time_month}{rand1}.{rand2}"
            elif i == 3:
                beacon_id += "k3:0000000000000000"
            elif i == 4:
                beacon_id += f"k4:{''.join(random.choices('123456789abcdef', k=16))}"
            else:
                beacon_id += f"k{i}:{random.randint(0, 9999)}"
            beacon_id += ";"
        return beacon_id

    @staticmethod
    def generate_random_imei() -> str:
        tac = random.randint(100000, 999999)
        snr = random.randint(100000, 999999)
        imei_without_checksum = f"{tac}{snr}"
        checksum = calculate_luhn_checksum(imei_without_checksum)
        return f"{imei_without_checksum}{checksum}"


class QIMEI:
    @staticmethod
    def generate_request_param(payload: dict) -> tuple[dict, str]:
        crypt_key = "".join(random.choices("adbcdef1234567890", k=16))
        nonce = "".join(random.choices("adbcdef1234567890", k=16))
        ts = int(time.time() * 1000)
        key = base64.b64encode(rsa_encrypt(crypt_key.encode())).decode()
        aes = AES(crypt_key.encode())
        params = base64.b64encode(aes.encrypt(json.dumps(payload).encode())).decode()
        extra = '{"appKey":"' + APP_KEY + '"}'
        sign = calculate_md5(
            key,
            params,
            str(ts),
            nonce,
            SECRET,
            extra,
        )
        data = {
            "app": 0,
            "os": 1,
            "qimeiParams": {
                "key": key,
                "params": params,
                "time": str(ts),
                "nonce": nonce,
                "sign": sign,
                "extra": extra,
            },
        }
        return data, str(int(ts / 1000))

    @staticmethod
    def get_qimei(app_version: str) -> QImeiResult:
        data, ts = QIMEI.generate_request_param(
            DeviceData.generate_random_payload(app_version)
        )
        sign = calculate_md5("qimei_qq_androidpzAuCmaFAaFaHrdakPjLIEqKrGnSOOvH", ts)
        try:
            res = requests.post(
                "https://api.tencentmusic.com/tme/trpc/proxy",
                headers={
                    "Host": "api.tencentmusic.com",
                    "method": "GetQimei",
                    "service": "trpc.tme_datasvr.qimeiproxy.QimeiProxy",
                    "appid": "qimei_qq_android",
                    "sign": sign,
                    "user-agent": "QQMusic",
                    "timestamp": ts,
                },
                json=data,
            )
            qimei_data = str(res.json()["data"])
            qimei = json.loads(qimei_data)
            return QImeiResult(qimei["data"]["q16"], qimei["data"]["q36"])
        except Exception:
            return QImeiResult(
                q16="fde9508748b00283b2723a9210001b617301",
                q36="35f21e7473442374591e560510001c71730b",
            )
