import pytest

from qqmusic_api.exceptions import LoginError
from qqmusic_api.login import PhoneLoginApi, PhoneLoginEvents, QQLoginApi, QrCodeLoginEvents, WXLoginApi

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_qq_login():
    qrsig, _ = await QQLoginApi.get_qrcode()
    state, _ = await QQLoginApi.check_qrcode_state(qrsig)
    assert state in [QrCodeLoginEvents.SCAN]


async def test_wx_login():
    uuid, _ = await WXLoginApi.get_qrcode()
    state, _ = await WXLoginApi.check_qrcode_state(uuid)
    assert state in [QrCodeLoginEvents.SCAN]


async def test_phone_login():
    phone = 17380269540
    state, _ = await PhoneLoginApi.send_authcode(phone)  # 号码为随机生成,仅用于测试
    assert state in [PhoneLoginEvents.SEND, PhoneLoginEvents.CAPTCHA]
    try:
        await PhoneLoginApi.authorize(phone, 123456)
    except LoginError:
        pass
