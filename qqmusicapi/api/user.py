import base64
import random
import re
import time
from typing import Any

import requests
from requests import Session

from qqmusicapi.exceptions import ParamsException
from qqmusicapi.utils import Utils


class User:
    @classmethod
    def login(
        cls,
        login_type: str = "get_qrcode",
        qrsig: str = "",
        pt_login_sig: str = "",
        ptsigx: str = "",
        uin: str = "",
    ) -> dict[str, Any]:
        """
        登录获取 cookies
        :param login_type: 登录类型
        :param qrsig: qrsig
        :param pt_login_sig: pt_login_sig
        :param ptsigx: ptsigx
        :param uin: uin
        :return:
        """
        if login_type == "get_qrcode":
            session = Session()
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
            session.get("https://xui.ptlogin2.qq.com/cgi-bin/xlogin", params=params)
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
            response = session.get(
                "https://ssl.ptlogin2.qq.com/ptqrshow", params=params
            )
            pt_login_sig = session.cookies.get("pt_login_sig")
            qrsig = session.cookies.get("qrsig")
            base64_img = base64.b64encode(response.content).decode("utf-8")
            print(
                f"http://127.0.0.1:5000/user/login?type=check_state&qrsig={qrsig}&pt_login_sig={pt_login_sig}"
            )
            return {
                "code": 200,
                "data": {
                    "pt_login_sig": pt_login_sig,
                    "qrsig": qrsig,
                    "img": f"data:image/png;base64,{base64_img}",
                },
            }
        elif login_type == "check_state":
            if not pt_login_sig or not qrsig:
                raise ParamsException("缺少必要参数")
            ptqrtoken = Utils.get_ptqrtoken(qrsig)
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
                "login_sig": pt_login_sig,
                "pt_uistyle": "40",
                "aid": "716027609",
                "daid": "383",
                "pt_3rd_aid": "100497308",
                "has_onekey": "1",
            }
            response = requests.get(
                "https://ssl.ptlogin2.qq.com/ptqrlogin",
                params=params,
                cookies={"pt_login_sig": pt_login_sig, "qrsig": qrsig},
            )
            if "二维码未失效" in response.text:
                state = 1
            elif "二维码认证中" in response.text:
                state = 2
            elif "二维码已失效" in response.text:
                state = 3
            else:
                state = 0
                qq_number = re.findall(r"&uin=(.+?)&service", response.text)[0]
                ptsigx = re.findall(r"&ptsigx=(.+?)&", response.text)[0]
                # print(response.text)
                return {
                    "code": 200,
                    "data": {"state": state, "qq_number": qq_number, "ptsigx": ptsigx},
                }
            return {"code": 200, "data": {"state": state}}
        elif login_type == "get_cookie":
            if not ptsigx or not uin:
                raise ParamsException("缺少必要参数")
            url = f"https://ssl.ptlogin2.graph.qq.com/check_sig?pttype=1&uin={uin}&service=ptqrlogin&nodirect=0&ptsigx={ptsigx}&s_url=https%3A%2F%2Fgraph.qq.com%2Foauth2.0%2Flogin_jump&f_url=&ptlang=2052&ptredirect=100&aid=716027609&daid=383&j_later=0&low_login_hour=0&regmaster=0&pt_login_type=3&pt_aid=0&pt_aaid=16&pt_light=0&pt_3rd_aid=100497308"
            response = requests.get(url, allow_redirects=False, verify=False)
            cookies = response.cookies
            p_skey = cookies.get("p_skey")
            g_tk = Utils.get_token(p_skey)
            uuid = Utils.get_uuid()
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
                "ui": uuid,
            }
            response = requests.post(
                "https://graph.qq.com/oauth2.0/authorize",
                params=params,
                data=data,
                allow_redirects=False,
                verify=False,
            )
            location = response.headers.get("Location", "")
            return {"code": 200, "data": {"location": location}}
        else:
            raise ParamsException("type 参数错误")
