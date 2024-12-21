"""登录相关 API"""

import random
import re
import time
import uuid
from enum import Enum, auto
from typing import Optional

import httpx

from .exceptions import LoginError, ResponseCodeError
from .utils.common import get_api, hash33
from .utils.credential import Credential
from .utils.network import Api

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

    刷新 cookies,刷新失败直接返回原始 credential,

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

    api = API["wx"]["login"] if credential.login_type == 1 else API["qq"]["login"]
    res = await Api(**api).update_params(**params).update_extra_common(tmeLoginType=str(credential.login_type)).result
    if res["code"] != 0:
        return credential
    return Credential.from_cookies_dict(res["data"])


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
    + FREQUENCY: 频繁操作
    + OTHER:   未知情况
    """

    SEND = auto()
    CAPTCHA = auto()
    FREQUENCY = auto()
    OTHER = auto()


class QQLoginApi:
    """QQ登录 API"""

    @staticmethod
    async def get_qrcode() -> tuple[str, bytes]:
        """获取二维码数据

        Returns:
            (qrsig,二维码二进制数据(PNG格式))
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
            raise LoginError("[QQLoginApi] 获取二维码失败")
        return qrsig, res.read()

    @staticmethod
    async def check_qrcode_state(qrsig: str) -> tuple[QrCodeLoginEvents, Optional[Credential]]:
        """检测二维码状态

        Args:
            qrsig: 二维码 qrsig

        Returns:
            (二维码状态, 扫码成功获取的用户凭证)

        Raises:
            LoginException: 获取失败
        """
        try:
            cookie = httpx.Cookies()
            cookie.set("qrsig", qrsig)
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
                .update_cookies(cookie)
                .request()
            )
        except httpx.HTTPStatusError:
            raise LoginError("[QQLoginApi] 无效 qrsig")

        match = re.search(r"ptuiCB\((.*?)\)", res.text)

        if not match:
            raise LoginError("[QQLoginApi] 获取二维码状态失败")
        data = [p.strip("'") for p in match.group(1).split(",")]
        code = data[0]
        event_map = {
            "68": QrCodeLoginEvents.REFUSE,
            "67": QrCodeLoginEvents.CONF,
            "66": QrCodeLoginEvents.SCAN,
            "65": QrCodeLoginEvents.TIMEOUT,
        }

        if code == "0":
            sigx = re.findall(r"&ptsigx=(.+?)&s_url", data[2])[0]
            uin = re.findall(r"&uin=(.+?)&service", data[2])[0]
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
                raise LoginError("[QQLoginApi] 获取 p_skey 失败")
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
                raise LoginError("[QQLoginApi] 获取 code 失败")

            response = (
                await Api(**API["qq"]["login"]).update_params(code=code).update_extra_common(tmeLoginType="2").result
            )

            if response["code"] == 0:
                return QrCodeLoginEvents.DONE, Credential.from_cookies_dict(response["data"])
            if response["code"] == 1000:
                raise LoginError("[QQLoginApi] 无法重复鉴权")
            raise LoginError("[QQLoginApi] 未知原因导致鉴权失败")

        return event_map.get(code, QrCodeLoginEvents.OTHER), None


class WXLoginApi:
    """微信登录 API"""

    @staticmethod
    async def get_qrcode() -> tuple[str, bytes]:
        """获取二维码数据

        Returns:
            (qrsig,二维码二进制数据(JEPG格式))
        """
        res = (
            await Api(**API["wx"]["get_qrcode"])
            .update_params(
                **{
                    "appid": "wx48db31d50e334801",
                    "redirect_uri": "https://y.qq.com/portal/wx_redirect.html?login_type=2&surl=https://y.qq.com/",
                    "response_type": "code",
                    "scope": "snsapi_login",
                    "state": "STATE",
                    "href": "https://y.qq.com/mediastyle/music_v17/src/css/popup_wechat.css#wechat_redirect",
                }
            )
            .request()
        )
        uuid = re.findall(r"uuid=(.+?)\"", res.text)[0]
        if not uuid:
            raise LoginError("[WXLoginApi] 获取 uuid 失败")
        qrcode_data = (
            await Api(
                url=f"https://open.weixin.qq.com/connect/qrcode/{uuid}",
            )
            .update_headers(Referer=str(res.url))
            .request()
        ).read()
        return uuid, qrcode_data

    @staticmethod
    async def check_qrcode_state(uuid: str) -> tuple[QrCodeLoginEvents, Optional[Credential]]:
        """检测二维码状态

        Args:
            uuid: 二维码 uuid

        Returns:
            (二维码状态, 二维码状态信息) 验证成功返回code(用于鉴权)

        Raises:
            LoginException: 获取失败
        """
        try:
            res = (
                await Api(**API["wx"]["check_qrcode_state"])
                .update_params(uuid=uuid, _=str(int(time.time()) * 1000))
                .request()
            )
        except httpx.TimeoutException:
            return QrCodeLoginEvents.SCAN, None

        match = re.search(r"window\.wx_errcode=(\d+);window\.wx_code=\'([^\']*)\'", res.text)
        if not match:
            raise LoginError("[WXLoginApi] 获取二维码状态失败")
        # 获取 wx_errcode 的值
        wx_errcode = match.group(1)
        # 获取 wx_code 的值
        wx_code = match.group(2)
        event_map = {
            "408": QrCodeLoginEvents.SCAN,
            "404": QrCodeLoginEvents.CONF,
            "403": QrCodeLoginEvents.REFUSE,
        }

        if wx_errcode == "405":
            if not wx_code:
                raise LoginError("[WXLoginApi] 获取 code 失败")

            response = (
                await Api(**API["wx"]["login"])
                .update_params(strAppid="wx48db31d50e334801", code=wx_code)
                .update_extra_common(tmeLoginType="1")
                .result
            )
            if response["code"] == 0:
                return QrCodeLoginEvents.DONE, Credential.from_cookies_dict(response["data"])
            if response["code"] == 1000:
                raise LoginError("[WXLoginApi] 无法重复鉴权")
            raise LoginError("[WXLoginApi] 未知原因导致鉴权失败")

        return event_map.get(wx_errcode, QrCodeLoginEvents.OTHER), None


class PhoneLoginApi:
    """手机号登录 API"""

    @staticmethod
    async def send_authcode(phone: int, country_code: int = 86) -> tuple[PhoneLoginEvents, str]:
        """发送验证码

        Args:
            phone: 手机号
            country_code: 国家码

        Returns:
            发送验证码状态,发送失败返回错误信息或验证链接
        """
        res = (
            await Api(**API["phone"]["send_authcode"])
            .update_params(
                **{
                    "tmeAppid": "qqmusic",
                    "phoneNo": str(phone),
                    "areaCode": str(country_code),
                }
            )
            .result
        )

        code = res["code"]
        if code == 20276:
            return PhoneLoginEvents.CAPTCHA, res["data"]["securityURL"]
        if code == 100001:
            return PhoneLoginEvents.FREQUENCY, ""
        if code == 0:
            return PhoneLoginEvents.SEND, ""
        return PhoneLoginEvents.OTHER, res["data"]["errMsg"]

    @staticmethod
    async def authorize(phone: int, auth_code: int, country_code: int = 86) -> Credential:
        """验证码鉴权

        只能鉴权一次,无法重复鉴权

        Args:
            phone: 手机号
            auth_code: 验证码
            country_code: 国家码

        Returns:
            登录凭证

        Raises:
            LoginError: 鉴权失败
        """
        res = (
            await Api(**API["phone"]["login"])
            .update_params(
                code=str(auth_code),
                phoneNo=str(phone),
                areaCode=str(country_code),
                loginMode=1,
            )
            .update_extra_common(tmeLoginMethod="3", tmeLoginType="0")
            .result
        )
        if res["code"] == 20271:
            raise LoginError("[PhoneLoginApi] 验证码错误或已鉴权")
        if res["code"] == 0:
            return Credential.from_cookies_dict(res["data"])
        raise LoginError("[PhoneLoginApi] 未知原因导致鉴权失败")
