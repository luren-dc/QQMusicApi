import asyncio
import subprocess
import sys

from qqmusic_api.login import PhoneLogin, PhoneLoginEvents


async def phone_login():
    phone = int(input("请输入手机号码"))
    login = PhoneLogin(phone)
    while 1:
        state = await login.send_authcode()
        if state == PhoneLoginEvents.SEND:
            print("发送成功")
            break
        elif state == PhoneLoginEvents.CAPTCHA:
            print("需要滑块验证", login.auth_url)
            print("验证后回车")
            if sys.platform == "win32":
                subprocess.call(["start", login.auth_url], shell=True)
            elif sys.platform == "darwin":
                subprocess.call(["open", login.auth_url])
            else:
                subprocess.call(["xdg-open", login.auth_url])
            input("")
        else:
            print("未知情况")
            return
    code = int(input("请输入验证码"))
    credential = await login.authorize(code)
    print(credential)


asyncio.run(phone_login())
