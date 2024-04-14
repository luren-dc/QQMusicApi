# 接口参数配置
# API接口
API_URL = "https://u.y.qq.com/cgi-bin/musicu.fcg"

# 随机
QIMEI36 = ""
UID = ""

# QQ音乐版本号
QQMUSIC_VERSION = ("13.2.5.8", "13020508")


def set_qimei(qimei: str):
    global QIMEI36
    if not QIMEI36:
        QIMEI36 = qimei


def set_uid(uid: str):
    global UID
    if not UID:
        UID = uid
