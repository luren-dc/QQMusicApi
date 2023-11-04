import asyncio
from io import BytesIO

import pytest
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

from pyqqmusicapi import QQMusic


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


async def login(type: int):
    api = QQMusic()
    async with api.login.request(type) as login:
        if type:
            print("请使用微信扫码")
        else:
            print("请使用QQ扫码")
        show_qrcode(await login.qrcode())
        while 1:
            state = await login.state()
            if state in [3, 4]:
                return 0
            elif state == 0:
                break
            await asyncio.sleep(1)
        return await login.authorize()


@pytest.mark.asyncio
async def test_qq(test_login, capfd):
    with capfd.disabled():
        assert await login(0)


@pytest.mark.asyncio
async def test_wx(test_login, capfd):
    with capfd.disabled():
        assert await login(1)
