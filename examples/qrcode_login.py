import asyncio

from qqmusic_api.login import (
    QR,
    LoginError,
    QRCodeLoginEvents,
    QRLoginType,
    check_qrcode,
    get_qrcode,
)


def show_qrcode(qr: QR):
    """显示二维码"""
    try:
        from io import BytesIO

        from PIL import Image
        from pyzbar.pyzbar import decode
        from qrcode import QRCode  # type: ignore

        img = Image.open(BytesIO(qr.data))
        url = decode(img)[0].data.decode("utf-8")
        qr = QRCode()
        qr.add_data(url)
        qr.print_ascii()
    except ImportError:
        # 保存二维码到当前目录
        save_path = qr.save()
        print(f"二维码已保存至: {save_path}")


async def qrcode_login_example(login_type: QRLoginType):
    """二维码登录示例"""

    try:
        # 1. 获取二维码
        qr = await get_qrcode(login_type)
        print(f"获取 {login_type.name} 二维码成功")

        show_qrcode(qr)

        # 2. 轮询检查扫码状态
        while True:
            event, credential = await check_qrcode(qr)
            print(f"当前状态: {event.name}")

            if event == QRCodeLoginEvents.DONE:
                print(f"登录成功! MusicID: {credential.musicid}")
                return credential
            if event == QRCodeLoginEvents.TIMEOUT:
                print("二维码已过期,请重新获取")
                break
            if event == QRCodeLoginEvents.SCAN:
                await asyncio.sleep(5)  # 5秒轮询一次
            else:
                await asyncio.sleep(2)

    except LoginError as e:
        print(f"登录失败: {e!s}")
    except Exception:
        raise


async def main():
    print("请选择登录方式:")
    print("1. QQ")
    print("2. WX")

    choice = input("请输入选项 (1/2): ").strip()

    if choice == "1":
        await qrcode_login_example(QRLoginType.QQ)
    elif choice == "2":
        await qrcode_login_example(QRLoginType.WX)
    else:
        print("无效的选项")


if __name__ == "__main__":
    asyncio.run(main())
