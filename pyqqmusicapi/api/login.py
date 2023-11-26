from __future__ import annotations

import random
import re
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, Dict, Optional

import aiohttp

if TYPE_CHECKING:
    from ..qqmusic import QQMusic

from ..utils import get_ptqrtoken, get_token, random_uuid


class Login(ABC):
    """登录抽象类"""

    parent: ClassVar[QQMusic]

    def __init__(self) -> None:
        super().__init__()
        self.musicid = ""
        self.auth_url = ""
        self.token: Dict = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/81.0.4044.129 Safari/537.36,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
                "Referer": "https://y.qq.com/",
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.session.close()

    @abstractmethod
    async def qrcode(self) -> bytes:
        """
        获取二维码

        Returns:
            二维码图像数据
        """

    @abstractmethod
    async def authcode(self) -> int:
        """
        发送验证码

        Returns:
            发送成功：0
            需要滑块验证：1
            未知情况：2
        """

    @abstractmethod
    async def state(self) -> int:
        """
        获取二维码状态

        Returns:
            登录成功: 0
            二维码未失效: 1,
            二维码认证中: 2,
            二维码已失效: 3,
            登录已被拒绝: 4,
        """

    @abstractmethod
    async def authorize(self, code: Optional[int] = None) -> bool:
        """
        登录验证

        Args:
            code: 验证码

        Returns:
            验证状态
        """


class QQLogin(Login):
    """QQ登录"""

    async def authcode(self) -> int:
        raise NotImplementedError("不支持获取验证码")

    async def qrcode(self):
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
        ) as response:
            self.sig = response.cookies.get("pt_login_sig").value
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
        ) as response:
            self.ptqrtoken = get_ptqrtoken(response.cookies.get("qrsig").value)
            return await response.read()

    async def state(self):
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
                "action": "0-0-%s" % int(time.time() * 1000),
                "js_ver": "20102616",
                "js_type": "1",
                "login_sig": self.sig,
                "pt_uistyle": "40",
                "aid": "716027609",
                "daid": "383",
                "pt_3rd_aid": "100497308",
                "has_onekey": "1",
            },
        ) as response:
            data = await response.text()
        response_text_to_state = {
            "二维码未失效": 1,
            "二维码认证中": 2,
            "二维码已失效": 3,
            "本次登录已被拒绝": 4,
            "登录成功": 0,
        }
        state = 5

        for text, value in response_text_to_state.items():
            if text in data:
                state = value
                break
        if state == 0:
            self.musicid = re.findall(r"&uin=(.+?)&service", data)[0]
            self.auth_url = re.findall(r"'(https:.*?)'", data)[0]
        return state

    async def authorize(self, code: Optional[int] = None) -> bool:
        async with self.session.get(self.auth_url, allow_redirects=False) as response:
            from http import cookies

            set_cookie_header = response.headers.getall("Set-Cookie", [])
            for header in set_cookie_header:
                cookie: cookies.SimpleCookie = cookies.SimpleCookie()
                cookie.load(header)
                for key, morsel in cookie.items():
                    if morsel.value:
                        self.session.cookie_jar.update_cookies(cookie)

        skey = self.session.cookie_jar.filter_cookies(self.auth_url).get("p_skey").value
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
                "g_tk": get_token(skey),
                "auth_time": str(int(time.time())),
                "ui": random_uuid(),
            },
            allow_redirects=False,
        ) as response:
            location = response.headers.get("Location", "")
            code = re.findall(r"(?<=code=)(.+?)(?=&)", location)[0]
        res = await self.parent.get_data(
            module="QQConnectLogin.LoginServer",
            method="QQLogin",
            param={"code": code},
            login_type="2",
        )
        if res.get("musickey", ""):
            self.token = res
            return True
        else:
            return False


class WXLogin(Login):
    """微信登录"""

    def __init__(self):
        super().__init__()
        self.uuid = ""

    async def authcode(self) -> int:
        raise NotImplementedError("不支持获取验证码")

    async def qrcode(self):
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
        ) as response:
            self.uuid = re.findall(r"uuid=(.+?)\"", await response.text())[0]
        async with self.session.get(
            f"https://open.weixin.qq.com/connect/qrcode/{self.uuid}",
            headers={
                "referer": "https://open.weixin.qq.com/connect/qrconnect?appid=wx48db31d50e334801"
                "&redirect_uri="
                "https%3A%2F%2Fy.qq.com%2Fportal%2Fwx_redirect.html%3Flogin_type%3D2%26surl%3Dhttps"
                "%3A%2F%2Fy.qq.com%2F"
                "&response_type=code&scope=snsapi_login&state=STATE"
                "&href=https%3A%2F%2Fy.qq.com%2Fmediastyle%2Fmusic_v17%2Fsrc%2Fcss%2Fpopup_wechat.css"
                "%23wechat_redirect"
            },
        ) as response:
            return await response.read()

    async def state(self):
        response_text_to_state = {
            "408": 1,
            "404": 2,
            "403": 4,
            "405": 0,
        }

        state = 5

        async with self.session.get(
            "https://lp.open.weixin.qq.com/connect/l/qrconnect",
            headers={
                "referer": "https://open.weixin.qq.com/",
            },
            params={
                "uuid": self.uuid,
                "_": str(int(round(time.time() * 1000))),
            },
        ) as response:
            for text, value in response_text_to_state.items():
                if text in await response.text():
                    state = value
                    break

            if state == 0:
                self.musicid = re.findall(r"wx_code='(.+?)';", await response.text())[0]
                self.auth_url = (
                    "https://y.qq.com/portal/wx_redirect.html?login_type=2"
                    f"&surl=https://y.qq.com/&code={self.musicid}&state=STATE"
                )
                await self.session.get(
                    "https://lp.open.weixin.qq.com/connect/l/qrconnect",
                    params={
                        "uuid": self.uuid,
                        "_": str(int(round(time.time() * 1000))),
                        "last": "404",
                    },
                )

        return state

    async def authorize(self, code: Optional[int] = None) -> bool:
        await self.session.get(self.auth_url, allow_redirects=False)
        res = await self.parent.get_data(
            module="music.login.LoginServer",
            method="Login",
            param={"strAppid": "wx48db31d50e334801", "code": self.musicid},
            login_type="1",
        )
        if res.get("musickey", ""):
            self.token = res
            return True
        else:
            return False


class PhoneLogin(Login):
    """手机号登录"""

    def __init__(self, phone: int):
        super().__init__()
        pattern = re.compile(r"^1[3-9]\d{9}$")
        if not pattern.match(str(phone)):
            raise ValueError("手机号非法")
        self.phone = phone
        self.security_url = None

    async def qrcode(self) -> bytes:
        raise NotImplementedError("不支持获取二维码")

    async def state(self) -> int:
        raise NotImplementedError("不支持获取二维码状态")

    async def authcode(self) -> int:
        res = await self.parent.get_data(
            module="music.login.LoginServer",
            method="SendPhoneAuthCode",
            param={
                "tmeAppid": "qqmusic",
                "phoneNo": str(self.phone),
                "areaCode": "86",
            },
        )
        msg = res["errMsg"]
        if msg == "OK":
            return 0
        elif msg == "robot defense":
            self.security_url = res["securityURL"]
            return 1
        else:
            return 2

    async def authorize(self, code: Optional[int] = None) -> bool:
        res = await self.parent.get_data(
            module="music.login.LoginServer",
            method="Login",
            param={"code": str(code), "phoneNo": str(self.phone), "loginMode": 1},
            login_method=3,
        )
        if res.get("musickey", ""):
            self.token = res
            return True
        else:
            return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class LoginApi:
    """登录Api"""

    parent: ClassVar[QQMusic]

    @staticmethod
    async def refresh(token: Dict) -> Dict:
        """
        刷新登录状态

        Args:
            token: 登录信息包括 openid、access_token、refresh_token、expired_in、musicid、musickey、refresh_key 和 login_type

        Returns:
            新的登录信息
        """
        response = await LoginApi.parent.get_data(
            module="music.login.LoginServer",
            method="Login",
            param={
                "openid": token.get("openid", ""),
                "access_token": token.get("access_token", ""),
                "refresh_token": token.get("refresh_token", ""),
                "expired_in": token.get("expired_in", 0),
                "musicid": token.get("musicid", ""),
                "musickey": token.get("musickey", ""),
                "refresh_key": token.get("refresh_key", ""),
                "loginMode": 2,
            },
            login_type=token.get("loginType", "2"),
        )
        if response.get("musickey", ""):
            return response
        else:
            return {}

    @staticmethod
    def request(login_type: int = 0, phone: Optional[int] = None) -> Login:
        """
        创建登录对象

        Args:
            login_type :
                登录类型
                QQ登录：0
                微信登录：1
                手机号登录：2
            phone: 手机号，仅在登录类型为2（手机号登录）时需要提供

        Returns:
            执行登录操作的具体对象
        """
        if login_type == 1:
            return WXLogin()
        elif login_type == 2:
            if not phone:
                raise ValueError("手机号为空")
            return PhoneLogin(phone)
        else:
            return QQLogin()
