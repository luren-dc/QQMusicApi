import asyncio

from qqmusic_api.login import QQLogin, QRCodeLogin, QrCodeLoginEvents


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
        state = await login.get_qrcode_state()

        if state == QrCodeLoginEvents.DONE:
            break
        elif state == QrCodeLoginEvents.TIMEOUT:
            show_qrcode(await login.get_qrcode())
        else:
            print("\r", state, "    ", end="")

        await asyncio.sleep(1)
    print("")
    credential = await login.authorize()
    print(credential)


async def main():
    logins = [
        QQLogin(),
        # WXLogin(),
    ]

    for login in logins:
        await qrcode_login(login)
        await login.close()


asyncio.run(main())
