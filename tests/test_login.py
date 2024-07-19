"""
使用`--test-login`测试登录Api
"""

import asyncio
from io import BytesIO

import pytest
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

from qqmusic_api.login import (
    Login,
    PhoneLogin,
    PhoneLoginEvents,
    QQLogin,
    QrCodeLoginEvents,
    WXLogin,
)

pytestmark = pytest.mark.asyncio(scope="module")


def show_qrcode(img_data):
    barcodes = decode(Image.open(BytesIO(img_data)))
    for barcode in barcodes:
        barcode_url = barcode.data.decode("utf-8")
    qr = qrcode.QRCode(
        version=2,
        box_size=12,
        border=1,
    )
    qr.add_data(barcode_url)
    # invert=True白底黑块,有些app不识别黑底白块.
    qr.print_ascii(invert=True)


async def login(login: Login):
    async with login:
        show_qrcode(await login.get_qrcode())
        while 1:
            await asyncio.sleep(1)
            state = await login.get_qrcode_state()
            if state in [
                QrCodeLoginEvents.TIMEOUT,
                QrCodeLoginEvents.REFUSE,
                QrCodeLoginEvents.OTHER,
            ]:
                print("登录失败")
                return
            elif state == QrCodeLoginEvents.DONE:
                break
            print("\r", state, end="")
        return await login.authorize()


@pytest.mark.timeout(50)
async def test_qq_login(is_test_login, capfd):
    with capfd.disabled():
        print("请使用QQ扫码")
        credential = await login(QQLogin())
        assert credential.has_musicid() and credential.has_musickey() and credential.can_refresh()


@pytest.mark.timeout(50)
async def test_wx_login(is_test_login, capfd):
    with capfd.disabled():
        print("请使用WX扫码")
        credential = await login(WXLogin())
        assert credential.has_musicid() and credential.has_musickey() and credential.can_refresh()


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
            input("")
        else:
            print("未知情况")
            return
    code = int(input("请输入验证码"))
    r = await login.authorize(code)
    assert r.musickey
