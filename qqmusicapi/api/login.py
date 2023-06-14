import random
import re
import time
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Dict
from uuid import uuid4

from requests import session

from qqmusicapi.exceptions import ParamsException, TypeException
from qqmusicapi.utils import Utils

# 登录类型
LOGIN_TYPE = ["QQ", "WX"]


class LoginRequest(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.login_type = ""
        self.cookies: Dict[str, Any] = {}
        self.refresh_url = ""
        self.login_id = str(uuid4()).replace("-", "")
        self.session = session()
        self.session.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/81.0.4044.129 Safari/537.36,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
                "referer": "https://y.qq.com/",
                "origin": "https://y.qq.com",
                "connection": "close",
            }
        )

    def get_login_id(self) -> str:
        """
        获取 loginID
        :return: loginID
        """
        return self.login_id

    def login(self, login_method: str) -> Any:
        """
        登录
        :param login_method: 登录方法
        :return:
        """
        try:
            return getattr(self, login_method)()
        except AttributeError:
            raise TypeException("登录方法错误")

    @abstractmethod
    def get_qrcode(self) -> BytesIO:
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_cookie(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _update_music_cookie(self, data: Dict[str, Any]):
        pass


class QQLoginRequest(LoginRequest):
    def __init__(self) -> None:
        super().__init__()
        self.login_type = "QQ"
        self.qrsig = ""
        self.pt_login_sig = ""

    def get_qrcode(self) -> BytesIO:
        self.session.get(
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
        )
        response = self.session.get(
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
        )
        self.pt_login_sig = self.session.cookies.get("pt_login_sig")
        self.qrsig = self.session.cookies.get("qrsig")
        return BytesIO(response.content)

    def get_state(self) -> Dict[str, Any]:
        if not self.qrsig:
            raise ParamsException("未获取登录二维码")
        ptqrtoken = Utils.get_ptqrtoken(self.qrsig)
        params = {
            "u1": "https://graph.qq.com/oauth2.0/login_jump",
            "ptqrtoken": str(ptqrtoken),
            "ptredirect": "0",
            "h": "1",
            "t": "1",
            "g": "1",
            "from_ui": "1",
            "ptlang": "2052",
            "action": f"0-0-{int(time.time() * 1000)}",
            "js_ver": "20102616",
            "js_type": "1",
            "login_sig": self.pt_login_sig,
            "pt_uistyle": "40",
            "aid": "716027609",
            "daid": "383",
            "pt_3rd_aid": "100497308",
            "has_onekey": "1",
        }
        response = self.session.get(
            "https://ssl.ptlogin2.qq.com/ptqrlogin", params=params
        )
        response_text_to_state = {
            "二维码未失效": 1,
            "二维码认证中": 2,
            "二维码已失效": 3,
            "本次登录已被拒绝": 4,
            "登录成功": 0,
        }
        state = 5

        for text, value in response_text_to_state.items():
            if text in response.text:
                state = value
                break

        if state == 0:
            uin = re.findall(r"&uin=(.+?)&service", response.text)[0]
            self.refresh_url = re.findall(r"'(https:.*?)'", response.text)[0]
            return {"state": state, "uin": uin}

        return {"state": state}

    def get_cookie(self) -> Dict[str, Any]:
        if not self.refresh_url:
            raise ParamsException("未登录")
        if self.cookies:
            return self.cookies

        self.session.get(self.refresh_url, allow_redirects=False)
        g_tk = Utils.get_token(self.session.cookies.get("p_skey"))

        response = self.session.post(
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
                "g_tk": g_tk,
                "auth_time": str(int(time.time())),
                "ui": Utils.get_uuid(),
            },
            allow_redirects=False,
        )

        location = response.headers.get("Location", "")

        self.session.get(
            location,
            headers={"Referer": "https://graph.qq.com/", "Host": "y.qq.com"},
        )

        code = re.findall(r"(?<=code=)(.+?)(?=&)", location)[0]
        self.session.headers.update(
            {
                "referer": "https://y.qq.com/",
                "origin": "https://y.qq.com",
            }
        )
        response = self.session.post(
            "https://u.y.qq.com/cgi-bin/musicu.fcg",
            data=Utils.format_data(
                {
                    "comm": {"g_tk": 5381, "platform": "yqq", "ct": 24, "cv": 0},
                    "req": {
                        "module": "QQConnectLogin.LoginServer",
                        "method": "QQLogin",
                        "param": {"code": code},
                    },
                }
            ),
        )
        data = response.json()["req"]["data"]
        self._update_music_cookie(data)
        return self.cookies

    def _update_music_cookie(self, data: Dict[str, Any]):
        self.cookies = {
            "code": 200,
            "data": {
                "uin": data["musicid"],
                "qqmusic_key": data["musickey"],
                "qm_keyst": data["musickey"],
                "psrf_qqrefresh_token": data["refresh_token"],
                "psrf_qqaccess_token": data["access_token"],
                "psrf_qqunionid": data["unionid"],
                "psrf_qqopenid": data["openid"],
            },
        }


class WXLoginRequest(LoginRequest):
    def __init__(self) -> None:
        super().__init__()
        self.login_type = "WX"
        self.uuid = ""
        self.wx_code = ""

    def get_qrcode(self) -> BytesIO:
        response = self.session.get(
            "https://open.weixin.qq.com/connect/qrconnect",
            params={
                "appid": "wx48db31d50e334801",
                "redirect_uri": "https://y.qq.com/portal/wx_redirect.html?login_type=2&surl=https://y.qq.com/",
                "response_type": "code",
                "scope": "snsapi_login",
                "state": "STATE",
                "href": "https://y.qq.com/mediastyle/music_v17/src/css/popup_wechat.css#wechat_redirect",
            },
        )
        self.uuid = re.findall(r"uuid=(.+?)\"", response.text)[0]
        self.session.headers.update(
            {
                "referer": "https://open.weixin.qq.com/connect/qrconnect?appid=wx48db31d50e334801"
                "&redirect_uri="
                "https%3A%2F%2Fy.qq.com%2Fportal%2Fwx_redirect.html%3Flogin_type%3D2%26surl%3Dhttps"
                "%3A%2F%2Fy.qq.com%2F"
                "&response_type=code&scope=snsapi_login&state=STATE"
                "&href=https%3A%2F%2Fy.qq.com%2Fmediastyle%2Fmusic_v17%2Fsrc%2Fcss%2Fpopup_wechat.css"
                "%23wechat_redirect"
            }
        )
        response = self.session.get(
            f"https://open.weixin.qq.com/connect/qrcode/{self.uuid}",
        )
        return BytesIO(response.content)

    def get_state(self) -> Dict[str, Any]:
        if not self.uuid:
            raise ParamsException("未获取登录二维码")
        self.session.headers.update(
            {
                "host": "lp.open.weixin.qq.com",
                "referer": "https://open.weixin.qq.com/",
            }
        )
        response = self.session.get(
            "https://lp.open.weixin.qq.com/connect/l/qrconnect",
            params={
                "uuid": self.uuid,
                "_": str(int(round(time.time() * 1000))),
            },
        )
        response_text_to_state = {
            "408": 1,
            "404": 2,
            "403": 4,
            "405": 0,
        }
        state = 5

        for text, value in response_text_to_state.items():
            if text in response.text:
                state = value
                break

        if state == 0:
            self.wx_code = re.findall(r"wx_code='(.+?)';", response.text)[0]
            self.refresh_url = (
                "https://y.qq.com/portal/wx_redirect.html?login_type=2"
                f"&surl=https://y.qq.com/&code={self.wx_code}&state=STATE"
            )
            params = {
                "uuid": self.uuid,
                "_": str(int(round(time.time() * 1000))),
                "last": "404",
            }
            self.session.get(
                "https://lp.open.weixin.qq.com/connect/l/qrconnect",
                params=params,
            )

        return {"state": state}

    def get_cookie(self) -> Dict[str, Any]:
        if not self.refresh_url:
            raise ParamsException("未登录")
        if self.cookies:
            return self.cookies

        self.session.get(self.refresh_url, allow_redirects=False)
        self.session.headers.update(
            {
                "referer": "https://y.qq.com/",
                "origin": "https://y.qq.com",
            }
        )
        print(self.session.headers)
        del self.session.headers["host"]
        response = self.session.post(
            "https://u.y.qq.com/cgi-bin/musicu.fcg",
            data=Utils.format_data(
                {
                    "comm": {
                        "tmeAppID": "qqmusic",
                        "tmeLoginType": "1",
                        "g_tk": 5381,
                        "platform": "yqq",
                        "ct": 24,
                        "cv": 0,
                    },
                    "req": {
                        "module": "music.login.LoginServer",
                        "method": "Login",
                        "param": {
                            "strAppid": "wx48db31d50e334801",
                            "code": self.wx_code,
                        },
                    },
                }
            ),
        )

        data = response.json()["req"]["data"]
        self._update_music_cookie(data)
        return self.cookies

    def _update_music_cookie(self, data: Dict[str, Any]):
        self.cookies = {
            "wxuin": data["musicid"],
            "qqmusic_key": data["musickey"],
            "qm_keyst": data["musickey"],
            "wxrefresh_token": data["refresh_token"],
            "wxunionid": data["unionid"],
            "wxopenid": data["openid"],
        }


def create_login_request(login_type: str) -> LoginRequest:
    """
    创建登录请求
    :param login_type: 登录类型
    :return: 请求实例
    """
    if login_type not in LOGIN_TYPE:
        raise TypeException("登录类型错误")
    if login_type == "QQ":
        qq_login_request = QQLoginRequest()
        return qq_login_request
    else:
        wx_login_request = WXLoginRequest()
        return wx_login_request
