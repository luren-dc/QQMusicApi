"""登录相关 API"""

import random
import re
import sys
import time
import uuid
from enum import Enum, auto

import httpx

if sys.version_info >= (3, 12):
    pass
else:
    pass

from .exceptions import LoginError, ResponseCodeError
from .utils.credential import Credential
from .utils.network import Api
from .utils.utils import get_api, hash33

API = get_api("login")


async def check_expired(credential: Credential) -> bool:
    """检查凭据是否过期

    Args:
        credential: 用户凭证

    Returns:
        是否过期
    """
    try:
        await Api(**API["check_expired"], credential=credential).result
        return False
    except ResponseCodeError:
        return True


async def refresh_cookies(credential: Credential) -> Credential:
    """刷新 Cookies

    刷新 cookies，刷新失败直接返回原始 credential,

    Note:
        刷新无效 cookie 需要 `refresh_key` 和 `refresh_token` 字段

    Args:
        credential: 用户凭证

    Returns:
        新的用户凭证
    """
    credential.raise_for_invalid()

    params = {
        "refresh_key": credential.refresh_key,
        "refresh_token": credential.refresh_token,
        "musickey": credential.musickey,
        "musicid": credential.musicid,
    }

    api = API["WX_login"] if credential.login_type == 1 else API["QQ_login"]
    try:
        res = (
            await Api(**api).update_params(**params).update_extra_common(tmeLoginType=str(credential.login_type)).result
        )
    except ResponseCodeError:
        return credential
    return Credential.from_cookies_dict(res)


class QrCodeLoginEvents(Enum):
    """二维码登录状态

    + SCAN:    等待扫描二维码
    + CONF:    已扫码未确认登录
    + TIMEOUT: 二维码已过期
    + DONE:    扫码成功
    + REFUSE:  拒绝登录
    + OTHER:   未知情况
    """

    DONE = auto()
    SCAN = auto()
    CONF = auto()
    TIMEOUT = auto()
    REFUSE = auto()
    OTHER = auto()


class PhoneLoginEvents(Enum):
    """手机登录状态

    + SEND:    发送成功
    + CAPTCHA: 需要滑块验证
    + OTHER:   未知情况
    """

    SEND = auto()
    CAPTCHA = auto()
    OTHER = auto()


class QQLogin:
    """QQ登录"""

    @staticmethod
    async def get_qrcode() -> tuple[str, bytes]:
        """获取二维码数据

        Returns:
            (qrsig,二维码二进制数据)
        """
        res = (
            await Api(**API["qq"]["get_qrcode"])
            .update_params(
                **{
                    "appid": "716027609",
                    "e": "2",
                    "l": "M",
                    "s": "3",
                    "d": "72",
                    "v": "4",
                    "t": str(random.random()),
                    "daid": "383",
                    "pt_3rd_aid": "100497308",
                }
            )
            .request()
        )
        qrsig = res.cookies.get("qrsig")
        if not qrsig:
            raise LoginError("[QQLogin] 获取二维码失败")
        return qrsig, res.read()

    @staticmethod
    async def check_qrcode_state(qrsig: str) -> tuple[QrCodeLoginEvents, dict]:
        """检测二维码状态

        Returns:
            (二维码状态, 二维码状态信息) 验证成功返回QQ号、QQ昵称、sigx(用于鉴权)

        Raises:
            LoginException: 无效 qrsig
        """
        try:
            res = (
                await Api(**API["qq"]["check_qrcode_state"])
                .update_params(
                    **{
                        "u1": "https://graph.qq.com/oauth2.0/login_jump",
                        "ptqrtoken": hash33(qrsig),
                        "ptredirect": "0",
                        "h": "1",
                        "t": "1",
                        "g": "1",
                        "from_ui": "1",
                        "ptlang": "2052",
                        "action": f"0-0-{time.time() * 1000}",
                        "js_ver": "20102616",
                        "js_type": "1",
                        "pt_uistyle": "40",
                        "aid": "716027609",
                        "daid": "383",
                        "pt_3rd_aid": "100497308",
                        "has_onekey": "1",
                    }
                )
                .update_headers(Cookie=f"qrsig={qrsig}")
                .request()
            )
        except httpx.HTTPStatusError:
            raise LoginError("[QQLogin] 无效 qrsig")

        match = re.search(r"ptuiCB\((.*?)\)", res.text)

        if not match:
            raise LoginError("[QQLogin] 获取二维码状态失败")
        data = [p.strip("'") for p in match.group(1).split(",")]
        code = data[0]
        if "0" == code:
            return QrCodeLoginEvents.DONE, {
                "uin": int(re.findall(r"&uin=(.+?)&service", data[2])[0]),
                "nick": data[-2],
                "sigx": re.findall(r"&ptsigx=(.+?)&s_url", data[2])[0],
            }
        elif "68" == code:
            return QrCodeLoginEvents.REFUSE, {}
        elif "67" == code:
            return QrCodeLoginEvents.CONF, {}
        elif "66" == code:
            return QrCodeLoginEvents.SCAN, {}
        elif "65" == code:
            return QrCodeLoginEvents.TIMEOUT, {}
        elif "67" == code:
            return QrCodeLoginEvents.CONF, {}
        else:
            return QrCodeLoginEvents.OTHER, {}

    @staticmethod
    async def authorize(uin: int, sigx: str) -> Credential:
        """登录鉴权

        只能鉴权一次，无法重复鉴权

        Args:
            uin:  QQ号
            sigx: 二维码扫码获得的sigx

        Returns:
            用户凭证

        Raises:
            LoginException: 鉴权失败
        """
        res = (
            await Api(**API["qq"]["check_sig"])
            .update_params(
                **{
                    "uin": str(uin),
                    "pttype": "1",
                    "service": "ptqrlogin",
                    "nodirect": "0",
                    "ptsigx": sigx,
                    "s_url": "https://graph.qq.com/oauth2.0/login_jump",
                    "ptlang": "2052",
                    "ptredirect": "100",
                    "aid": "716027609",
                    "daid": "383",
                    "j_later": "0",
                    "low_login_hour": "0",
                    "regmaster": "0",
                    "pt_login_type": "3",
                    "pt_aid": "0",
                    "pt_aaid": "16",
                    "pt_light": "0",
                    "pt_3rd_aid": "100497308",
                }
            )
            .request()
        )

        p_skey = res.cookies.get("p_skey")

        if not p_skey:
            raise LoginError("[QQLogin] 获取 p_skey 失败")
        res = await (
            Api(**API["qq"]["authorize"])
            .update_data(
                **{
                    "response_type": "code",
                    "client_id": "100497308",
                    "redirect_uri": "https://y.qq.com/portal/wx_redirect.html?login_type=1&surl=https%3A%252F%252Fy.qq.com%252F",
                    "scope": "get_user_info,get_app_friends",
                    "state": "state",
                    "switch": "",
                    "from_ptlogin": "1",
                    "src": "1",
                    "update_auth": "1",
                    "openapi": "1010_1030",
                    "g_tk": hash33(p_skey, 5381),
                    "auth_time": str(int(time.time()) * 1000),
                    "ui": str(uuid.uuid4()),
                },
            )
            .update_cookies(res.cookies)
            .request()
        )

        location = res.headers.get("Location", "")
        try:
            code = re.findall(r"(?<=code=)(.+?)(?=&)", location)[0]
        except IndexError:
            raise LoginError("[QQLogin] 获取 code 失败")

        response = await Api(**API["qq"]["login"]).update_params(code=code).update_extra_common(tmeLoginType="2").result

        if response["code"] == 0:
            return Credential.from_cookies_dict(response["data"])
        elif response["code"] == 1000:
            raise LoginError("[QQLogin] 无法重复鉴权")
        else:
            raise LoginError("[QQLogin] 未知原因导致鉴权失败")
