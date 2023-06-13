import random
import re
import time
import uuid
from io import BytesIO
from typing import Any

import requests

from qqmusicapi.exceptions import ParamsException, TypeException
from qqmusicapi.utils import Utils


class Login:
    def __init__(self):
        self.refresh_url = ""
        self.qrsig = ""
        self.key = ""
        self.uin = 0
        self.keyst = ""
        self.session = requests.session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/81.0.4044.129 Safari/537.36,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
                "Referer": "https://y.qq.com/",
            }
        )

    def login(self, login_type: str) -> dict[str, Any]:
        try:
            login_method = getattr(self, login_type)
            return login_method()
        except AttributeError:
            raise TypeException("登录方法错误")

    def get_qrcode(self) -> BytesIO:
        params = {
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
        }
        self.session.get("https://xui.ptlogin2.qq.com/cgi-bin/xlogin", params=params)
        params = {
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
        response = self.session.get(
            "https://ssl.ptlogin2.qq.com/ptqrshow", params=params
        )
        img = BytesIO(response.content)
        self.pt_login_sig = self.session.cookies.get("pt_login_sig")
        self.qrsig = self.session.cookies.get("qrsig")
        return img

    def check_state(self) -> dict[str, Any]:
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
            "action": "0-0-%s" % int(time.time() * 1000),
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
        if "二维码未失效" in response.text:
            state = 1
        elif "二维码认证中" in response.text:
            state = 2
        elif "二维码已失效" in response.text:
            state = 3
        else:
            state = 0
            uin = re.findall(r"&uin=(.+?)&service", response.text)[0]
            self.refresh_url = re.findall(r"'(https:.*?)'", response.text)[0]
            return {
                "code": 200,
                "data": {
                    "state": state,
                    "uin": uin,
                },
            }
        return {"code": 200, "data": {"state": state}}

    def get_cookie(self) -> dict[str, Any]:
        if not self.refresh_url:
            raise ParamsException("未登录")
        if self.key:
            return {
                "code": 200,
                "data": {
                    "uin": self.uin,
                    "qqmusic_key": self.key,
                    "qm_keyst": self.keyst,
                },
            }
        self.session.get(self.refresh_url, allow_redirects=False)
        g_tk = Utils.get_token(self.session.cookies.get("p_skey"))
        params = {
            "Referer": "https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id"
            "=100497308&redirect_uri=https://y.qq.com/portal/wx_redirect.html?login_type=1&surl=https"
            "://y.qq.com/portal/profile.html#stat=y_new.top.user_pic&stat=y_new.top.pop.logout"
            "&use_customer_cb=0&state=state&display=pc",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
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
        }
        response = self.session.post(
            "https://graph.qq.com/oauth2.0/authorize",
            params=params,
            data=data,
            allow_redirects=False,
        )
        location = response.headers.get("Location", "")
        self.session.get(
            location,
            headers={"Referer": "https://graph.qq.com/", "Host": "y.qq.com"},
        )
        code = re.findall(r"(?<=code=)(.+?)(?=&)", location)[0]
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate",
            "Host": "u.y.qq.com",
            "Origin": "https://y.qq.com",
        }
        data = {
            "comm": {"g_tk": 5381, "platform": "yqq", "ct": 24, "cv": 0},
            "req": {
                "module": "QQConnectLogin.LoginServer",
                "method": "QQLogin",
                "param": {"code": code},
            },
        }
        response = self.session.post(
            "https://u.y.qq.com/cgi-bin/musicu.fcg",
            data=Utils.format_data(data),
            headers=headers,
        )
        cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        self.uin = cookies["uin"]
        self.key = cookies["qqmusic_key"]
        self.keyst = cookies["qm_keyst"]

        return {
            "code": 200,
            "data": {
                "uin": self.uin,
                "qqmusic_key": self.key,
                "qm_keyst": self.keyst,
                "cooke": cookies,
            },
        }

    def get_login_id(self) -> str:
        self.login_id = str(uuid.uuid4())
        self.login_id = self.login_id.replace("-", "")
        return self.login_id
