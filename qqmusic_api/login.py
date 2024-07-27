"""登录相关 API"""

import random
import re
import time
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import aiohttp
from typing_extensions import override

from .exceptions import LoginException, ResponseCodeException
from .utils.credential import Credential
from .utils.network import Api
from .utils.utils import get_api, hash33

API = get_api("login")


class QrCodeLoginEvents(Enum):
    """二维码登录状态

    + SCAN:    未扫描二维码
    + CONF:    未确认登录
    + TIMEOUT: 二维码过期
    + DONE:    成功
    + REFUSE:  拒绝登录
    + OTHER:   未知情况
    """

    DONE = 0
    SCAN = 1
    CONF = 2
    TIMEOUT = 3
    REFUSE = 4
    OTHER = 5


class PhoneLoginEvents(Enum):
    """手机登录状态

    + SEND:    发送成功
    + CAPTCHA: 需要滑块验证
    + OTHER:   未知情况
    """

    SEND = 0
    CAPTCHA = 1
    OTHER = 5


class Login:
    """登录基类

    Attributes:
        auth_url: 验证链接，用于鉴权和滑块验证
        credential: 用户凭证
    """

    def __init__(self) -> None:
        self.auth_url: Optional[str] = None
        self.credential: Optional[Credential] = None


class QRCodeLogin(Login, ABC):
    """二维码登录基类

    Attributes:
        musicid: 登录账号
    """

    def __init__(self) -> None:
        super().__init__()
        self.musicid = ""
        self._state: Optional[QrCodeLoginEvents] = None
        self._qrcode_data: Optional[bytes] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self.session.closed:
            await self.session.close()

    @abstractmethod
    async def get_qrcode(self) -> bytes:
        """获取二维码

        Returns:
            二维码二进制数据
        """

    @abstractmethod
    async def get_qrcode_state(self) -> QrCodeLoginEvents:
        """获取二维码状态

        Returns:
            二维码状态

        Raises:
            LoginException: 未获取二维码
        """

    @abstractmethod
    async def authorize(self) -> Credential:
        """登录鉴权

        Returns:
            用户凭证

        Raises:
            LoginException: 未完成二维码认证
        """


# TODO: 优化扫码登录流程
class QQLogin(QRCodeLogin):
    """QQ登录"""

    @override
    async def get_qrcode(self):
        if self._qrcode_data and self._state not in [
            QrCodeLoginEvents.TIMEOUT,
            QrCodeLoginEvents.REFUSE,
            QrCodeLoginEvents.DONE,
        ]:
            return self._qrcode_data
        async with self.session.get(
            "https://xui.ptlogin2.qq.com/cgi-bin/xlogin",
            params={
                "appid": "716027609",
                "daid": "383",
                "style": "33",
                "login_text": "登录",
                "hide_title_bar": "1",
                "hide_border": "1",
                "target": "self",
                "s_url": "https://graph.qq.com/oauth2.0/login_jump",
                "pt_3rd_aid": "100497308",
                "pt_feedback_link": "https://support.qq.com/products/77942?customInfo=.appid100497308",
                "theme": "2",
                "verify_theme": "",
            },
        ) as res:
            self.sig = res.cookies.get("pt_login_sig").value
        async with self.session.get(
            "https://ssl.ptlogin2.qq.com/ptqrshow",
            params={
                "appid": "716027609",
                "e": "2",
                "l": "M",
                "s": "3",
                "d": "72",
                "v": "4",
                "t": str(random.random()),
                "daid": "383",
                "pt_3rd_aid": "100497308",
            },
        ) as res:
            self.ptqrtoken = hash33(res.cookies.get("qrsig").value)
            self._qrcode_data = await res.read()
            return self._qrcode_data

    @override
    async def get_qrcode_state(self):
        if not self._qrcode_data:
            raise LoginException("请先获取二维码")
        async with self.session.get(
            "https://ssl.ptlogin2.qq.com/ptqrlogin",
            params={
                "u1": "https://graph.qq.com/oauth2.0/login_jump",
                "ptqrtoken": self.ptqrtoken,
                "ptredirect": "0",
                "h": "1",
                "t": "1",
                "g": "1",
                "from_ui": "1",
                "ptlang": "2052",
                "action": f"0-0-{int(time.time() * 1000)}",
                "js_ver": "20102616",
                "js_type": "1",
                "login_sig": self.sig,
                "pt_uistyle": "40",
                "aid": "716027609",
                "daid": "383",
                "pt_3rd_aid": "100497308",
                "has_onekey": "1",
            },
        ) as res:
            data = await res.text()
        text_to_state = {
            "二维码未失效": QrCodeLoginEvents.SCAN,
            "二维码认证中": QrCodeLoginEvents.CONF,
            "二维码已失效": QrCodeLoginEvents.TIMEOUT,
            "本次登录已被拒绝": QrCodeLoginEvents.REFUSE,
            "登录成功": QrCodeLoginEvents.DONE,
        }
        state = QrCodeLoginEvents.OTHER
        for text, value in text_to_state.items():
            if text in data:
                state = value
                break
        self._state = state
        if state == QrCodeLoginEvents.DONE:
            self.musicid = re.findall(r"&uin=(.+?)&service", data)[0]
            self.auth_url = re.findall(r"'(https:.*?)'", data)[0]
        return state

    @override
    async def authorize(self):
        if self.credential:
            return self.credential
        if self._state != QrCodeLoginEvents.DONE:
            raise LoginException("未完成二维码认证")
        # TODO: 优化获取 p_skey
        async with self.session.get(self.auth_url, allow_redirects=False) as res:  # type: ignore
            from http import cookies

            set_cookie_header = res.headers.getall("Set-Cookie", [])
            for header in set_cookie_header:
                cookie: cookies.SimpleCookie = cookies.SimpleCookie()
                cookie.load(header)
                for key, morsel in cookie.items():
                    if morsel.value:
                        self.session.cookie_jar.update_cookies(cookie)

        skey = self.session.cookie_jar.filter_cookies(self.auth_url).get("p_skey").value  # type: ignore
        async with self.session.post(
            "https://graph.qq.com/oauth2.0/authorize",
            params={
                "Referer": "https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id"
                "=100497308&redirect_uri=https://y.qq.com/portal/wx_redirect.html?login_type=1&surl=https"
                "://y.qq.com/portal/profile.html#stat=y_new.top.user_pic&stat=y_new.top.pop.logout"
                "&use_customer_cb=0&state=state&display=pc",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "response_type": "code",
                "client_id": "100497308",
                "redirect_uri": "https://y.qq.com/portal/wx_redirect.html?login_type=1&surl=https://y.qq.com"
                "/#&use_customer_cb=0",
                "scope": "",
                "state": "state",
                "switch": "",
                "from_ptlogin": "1",
                "src": "1",
                "update_auth": "1",
                "openapi": "80901010",
                "g_tk": hash33(skey, 5381),
                "auth_time": str(int(time.time())),
                "ui": uuid.uuid4(),
            },
            allow_redirects=False,
        ) as res:
            location = res.headers.get("Location", "")
            code = re.findall(r"(?<=code=)(.+?)(?=&)", location)[0]
        res = await Api(**API["QQ_login"]).update_params(code=code).update_extra_common(tmeLoginType="2").result
        self.credential = Credential.from_cookies(res)
        return self.credential


class WXLogin(QRCodeLogin):
    """微信登录"""

    def __init__(self):
        super().__init__()
        self.__uuid = ""

    @override
    async def get_qrcode(self):
        if self._qrcode_data and self._state not in [
            QrCodeLoginEvents.TIMEOUT,
            QrCodeLoginEvents.REFUSE,
            QrCodeLoginEvents.DONE,
        ]:
            return self._qrcode_data
        async with self.session.get(
            "https://open.weixin.qq.com/connect/qrconnect",
            params={
                "appid": "wx48db31d50e334801",
                "redirect_uri": "https://y.qq.com/portal/wx_redirect.html?login_type=2&surl=https://y.qq.com/",
                "response_type": "code",
                "scope": "snsapi_login",
                "state": "STATE",
                "href": "https://y.qq.com/mediastyle/music_v17/src/css/popup_wechat.css#wechat_redirect",
            },
        ) as res:
            self.__uuid = re.findall(r"uuid=(.+?)\"", await res.text())[0]
        async with self.session.get(
            f"https://open.weixin.qq.com/connect/qrcode/{self.__uuid}",
            headers={
                "referer": "https://open.weixin.qq.com/connect/qrconnect?appid=wx48db31d50e334801"
                "&redirect_uri="
                "https%3A%2F%2Fy.qq.com%2Fportal%2Fwx_redirect.html%3Flogin_type%3D2%26surl%3Dhttps"
                "%3A%2F%2Fy.qq.com%2F"
                "&response_type=code&scope=snsapi_login&state=STATE"
                "&href=https%3A%2F%2Fy.qq.com%2Fmediastyle%2Fmusic_v17%2Fsrc%2Fcss%2Fpopup_wechat.css"
                "%23wechat_redirect"
            },
        ) as res:
            self._qrcode_data = await res.read()
            return self._qrcode_data

    @override
    async def get_qrcode_state(self):
        if not self._qrcode_data:
            raise LoginException("请先获取二维码")
        async with self.session.get(
            "https://lp.open.weixin.qq.com/connect/l/qrconnect",
            headers={
                "referer": "https://open.weixin.qq.com/",
            },
            params={
                "uuid": self.__uuid,
                "_": str(int(round(time.time() * 1000))),
            },
        ) as res:
            data = await res.text()

        text_to_state = {
            "408": QrCodeLoginEvents.SCAN,
            "404": QrCodeLoginEvents.CONF,
            "403": QrCodeLoginEvents.REFUSE,
            "405": QrCodeLoginEvents.DONE,
        }
        state = QrCodeLoginEvents.OTHER
        for text, value in text_to_state.items():
            if text in await res.text():
                state = value
                break
        self._state = state
        if state == QrCodeLoginEvents.DONE:
            self.musicid = re.findall(r"wx_code='(.+?)';", data)[0]
            self.auth_url = (
                "https://y.qq.com/portal/wx_redirect.html?login_type=2"
                f"&surl=https://y.qq.com/&code={self.musicid}&state=STATE"
            )
            await self.session.get(
                "https://lp.open.weixin.qq.com/connect/l/qrconnect",
                params={
                    "uuid": self.__uuid,
                    "_": str(int(round(time.time() * 1000))),
                    "last": "404",
                },
            )
        return state

    @override
    async def authorize(self):
        if self.credential:
            return self.credential
        if self._state != QrCodeLoginEvents.DONE:
            raise LoginException("未完成二维码认证")
        await self.session.get(self.auth_url, allow_redirects=False)  # type: ignore
        res = (
            await Api(**API["WX_login"])
            .update_params(strAppid="wx48db31d50e334801", code=self.musicid)
            .update_extra_common(tmeLoginType="1")
            .result
        )
        self.credential = Credential.from_cookies(res)
        return self.credential


class PhoneLogin(Login):
    """手机号登录

    Attributes:
        phone: 手机号码
    """

    def __init__(self, phone: str):
        """初始化手机号登录类

        Args:
            phone: 手机号码

        Raises:
            ValueError: 非法手机号
        """
        if not re.compile(r"^1[3-9]\d{9}$").match(phone):
            raise ValueError("非法手机号")
        self.phone = phone

    async def send_authcode(self) -> PhoneLoginEvents:
        """发送验证码

        Returns:
            操作状态
        """
        params = {
            "tmeAppid": "qqmusic",
            "phoneNo": str(self.phone),
            "areaCode": "86",
        }
        try:
            await Api(**API["send_authcode"]).update_params(**params).result
            return PhoneLoginEvents.SEND
        except ResponseCodeException as e:
            if e.code == 20276:
                self.auth_url = e.raw["securityURL"]  # type: ignore
                return PhoneLoginEvents.CAPTCHA
            else:
                return PhoneLoginEvents.OTHER

    async def authorize(self, authcode: int) -> Credential:
        """登录鉴权

        Args:
            authcode: 验证码

        Returns:
            用户凭证

        Raises:
            LoginException: 鉴权失败
        """
        if not authcode:
            raise ValueError("authcode 为空")
        params = {"code": str(authcode), "phoneNo": self.phone, "loginMode": 1}
        try:
            res = (
                await Api(**API["phone_login"])
                .update_params(**params)
                .update_extra_common(tmeLoginMethod="3", tmeLoginType="0")
                .result
            )
        except ResponseCodeException as e:
            if e.code == 20271:
                raise LoginException("验证码过期或错误")
            else:
                raise LoginException("未知情况，请提交 issue")
        return Credential.from_cookies(res)


async def refresh_cookies(credential: Credential) -> Credential:
    """刷新 Cookies

    Args:
        credential: 用户凭证

    Return:
        新的用户凭证
    """
    credential.raise_for_cannot_refresh()
    params = {
        "refresh_key": credential.refresh_key,
        "musicid": credential.musicid,
        "loginMode": 2,
    }
    res = (
        await Api(**API["refresh"])
        .update_params(**params)
        .update_extra_common(tmeLoginType=str(credential.login_type))
        .result
    )
    return Credential.from_cookies(res)
