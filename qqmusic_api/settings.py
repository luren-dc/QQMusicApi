from .utils.common import random_string
from .utils.qimei import Qimei

# 接口参数配置
# API接口
API_URL = "https://u.y.qq.com/cgi-bin/musicu.fcg"

# 随机
QIMEI36 = ""
UID = ""

# QQ音乐版本号
QQMUSIC_VERSION = ["13.2.5.8", "13020508"]


def get_qimei() -> str:
    """
    获取Qimei
    """
    global QIMEI36
    if not QIMEI36:
        result = Qimei.get()
        QIMEI36 = result.q36 if result.q36 else "cc8d07a748d4be0a8b91eacd100014a1730e"
    return QIMEI36


def get_uid() -> str:
    global UID
    if not UID:
        UID = random_string(10, "0123456789")
    return UID
