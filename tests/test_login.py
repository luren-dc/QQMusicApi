import pytest

from qqmusic_api.exceptions import LoginException
from qqmusic_api.login import PhoneLogin, PhoneLoginEvents, QQLogin, QrCodeLoginEvents, WXLogin

pytestmark = pytest.mark.asyncio(scope="package")


async def test_qq_login():
    async with QQLogin() as login:
        await login.get_qrcode()
        state = await login.get_qrcode_state()
        assert state in [QrCodeLoginEvents.SCAN]


async def test_wx_login():
    async with WXLogin() as login:
        await login.get_qrcode()
        state = await login.get_qrcode_state()
        assert state in [QrCodeLoginEvents.SCAN]


async def test_phone_login():
    login = PhoneLogin("17380269540")  # 号码为随机生成，仅用于测试
    state = await login.send_authcode()
    assert state in [PhoneLoginEvents.SEND, PhoneLoginEvents.CAPTCHA]
    try:
        await login.authorize(123456)
    except LoginException:
        pass
