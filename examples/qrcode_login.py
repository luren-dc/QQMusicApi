import asyncio

from qqmusic_api.login_utils import QQLogin, QRCodeLogin, QrCodeLoginEvents


def show_qrcode(data: bytes):
    """显示二维码"""
    try:
        from io import BytesIO

        from PIL import Image
        from pyzbar.pyzbar import decode
        from qrcode import QRCode  # type: ignore

        img = Image.open(BytesIO(data))
        url = decode(img)[0].data.decode("utf-8")
        qr = QRCode()
        qr.add_data(url)
        qr.print_ascii()
    except ImportError:
        with open("qrcode.png", "wb") as f:
            f.write(data)
        print("请在 qrcode.png 中查看二维码")


async def qrcode_login(login: QRCodeLogin):
    """二维码登录"""
    print(login.__class__.__name__)
    show_qrcode(await login.get_qrcode())
    while True:
        state, credential = await login.check_qrcode_state()
        if state == QrCodeLoginEvents.REFUSE:
            print("拒绝登录")
            exit()
        elif state == QrCodeLoginEvents.TIMEOUT:
            print("二维码过期")
            exit()
        elif state == QrCodeLoginEvents.CONF:
            print("\r请确认登录", end="")
        elif state == QrCodeLoginEvents.SCAN:
            print("\r请扫描二维码", end="")
        elif state == QrCodeLoginEvents.DONE:
            print("\n登录成功")
            break

        await asyncio.sleep(4)

    # 获取Credential
    # login.credential
    print(credential)


asyncio.run(qrcode_login(QQLogin()))
