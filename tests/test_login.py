import pytest

from qqmusic_api.exceptions import LoginError
from qqmusic_api.login import (
    PhoneLoginEvents,
    QRCodeLoginEvents,
    QRLoginType,
    check_qrcode,
    get_qrcode,
    phone_authorize,
    send_authcode,
)

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_qq_login():
    qr = await get_qrcode(QRLoginType.QQ)
    state, _ = await check_qrcode(qr)
    assert state in [QRCodeLoginEvents.SCAN]


async def test_wx_login():
    qr = await get_qrcode(QRLoginType.WX)
    state, _ = await check_qrcode(qr)
    assert state in [QRCodeLoginEvents.SCAN]


async def test_phone_login():
    phone = 17380269540
    state, _ = await send_authcode(phone)  # 号码为随机生成,仅用于测试
    assert state in [PhoneLoginEvents.SEND, PhoneLoginEvents.CAPTCHA]
    with pytest.raises(LoginError):
        await phone_authorize(phone, 123456)
