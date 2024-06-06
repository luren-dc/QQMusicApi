from .utils.common import random_string
from .utils.qimei import Qimei

# 接口参数配置
# API接口
API_URL = "https://u.y.qq.com/cgi-bin/musicu.fcg"

# QQ音乐版本号
QQMUSIC_VERSION = "13.2.5.8"
QQMUSIC_VERSION_CODE = 13020508


def get_qimei36(version):
    result = Qimei.get(version)
    if result.q36:
        return result.q36
    else:
        return "cc8d07a748d4be0a8b91eacd100014a1730e"


QIMEI36 = get_qimei36(QQMUSIC_VERSION)
UID = random_string(10, "0123456789")
