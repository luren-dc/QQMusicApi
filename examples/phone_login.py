import asyncio

from qqmusic_api.login import (
    LoginError,
    PhoneLoginEvents,
    phone_authorize,
    send_authcode,
)


async def phone_login_example():
    """手机验证码登录示例"""
    phone = 17385716325
    country_code = 86

    try:
        # 1. 发送验证码
        event, info = await send_authcode(phone, country_code)

        if event == PhoneLoginEvents.CAPTCHA:
            print(f"需要验证,访问链接: {info}")
            return None
        if event == PhoneLoginEvents.FREQUENCY:
            print("操作过于频繁,请稍后再试")
            return None

        print("验证码已发送")

        # 2. 获取用户输入
        auth_code = input("请输入验证码: ").strip()

        # 3. 执行登录
        credential = await phone_authorize(phone, int(auth_code), country_code)
        print(f"登录成功! MusicID: {credential.musicid}")
        return credential

    except LoginError as e:
        print(f"登录失败: {e!s}")
    except ValueError:
        print("验证码必须为6位数字")
    except Exception as e:
        print(f"发生未知错误: {e!s}")


asyncio.run(phone_login_example())
