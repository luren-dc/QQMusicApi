"""登录相关 Utils

对登录Api的进一步封装
"""

import sys
from abc import ABC, abstractmethod
from typing import Optional

from .exceptions.api_exception import LoginError

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from .login import PhoneLoginApi, PhoneLoginEvents, QQLoginApi, QrCodeLoginEvents, WXLoginApi
from .utils.credential import Credential


class Login(ABC):
    """登录基类

    Attributes:
        credential: 用户凭证
    """

    def __init__(self) -> None:
        self.credential: Optional[Credential] = None


class QRCodeLogin(Login):
    """二维码登录基类"""

    def __init__(self) -> None:
        super().__init__()
        self._state: Optional[QrCodeLoginEvents] = None
        self._qrcode_data: Optional[bytes] = None

    @abstractmethod
    async def get_qrcode(self) -> bytes:
        """获取二维码

        Returns:
            二维码二进制数据(QQ:PNG格式,WX:JEPG格式)
        """

    @abstractmethod
    async def check_qrcode_state(self) -> tuple[QrCodeLoginEvents, Optional[Credential]]:
        """检测二维码状态

        Returns:
            二维码状态,扫码成功返回凭证
        """


class QQLogin(QRCodeLogin):
    """QQ 登录"""

    def __init__(self) -> None:
        super().__init__()
        self._qrsig = ""

    @override
    async def get_qrcode(self) -> bytes:
        if self._qrcode_data and self._state in (QrCodeLoginEvents.CONF, QrCodeLoginEvents.SCAN):
            return self._qrcode_data
        self._qrsig, self._qrcode_data = await QQLoginApi.get_qrcode()
        return self._qrcode_data

    @override
    async def check_qrcode_state(self) -> tuple[QrCodeLoginEvents, Optional[Credential]]:
        if self._state == QrCodeLoginEvents.DONE and self.credential:
            return self._state, self.credential
        if not self._qrsig:
            raise LoginError("[QQLogin] 请先获取二维码")
        self._state, self.credential = await QQLoginApi.check_qrcode_state(self._qrsig)
        return self._state, self.credential


class WXLogin(QRCodeLogin):
    """微信 登录"""

    def __init__(self) -> None:
        super().__init__()
        self._uuid = ""
        self._code = ""

    @override
    async def get_qrcode(self) -> bytes:
        if self._qrcode_data and self._state in (QrCodeLoginEvents.CONF, QrCodeLoginEvents.SCAN):
            return self._qrcode_data
        self._uuid, self._qrcode_data = await WXLoginApi.get_qrcode()
        return self._qrcode_data

    @override
    async def check_qrcode_state(self) -> tuple[QrCodeLoginEvents, Optional[Credential]]:
        if self._state == QrCodeLoginEvents.DONE and self.credential:
            return self._state, self.credential
        if not self._uuid:
            raise LoginError("[WXLogin] 请先获取二维码")
        self._state, self.credential = await WXLoginApi.check_qrcode_state(self._uuid)
        return self._state, self.credential


class PhoneLogin(Login):
    """手机号登录

    Attributes:
        phone: 手机号
        area_code: 国家码
        auth_url: 验证链接
        error_msg: 错误信息
    """

    def __init__(self, phone: int, area_code: int = 86) -> None:
        super().__init__()
        self.phone = phone
        self.area_code = area_code
        self.auth_url = ""
        self._state: Optional[PhoneLoginEvents] = None
        self.error_msg = ""

    async def send_authcode(self) -> PhoneLoginEvents:
        """发送验证码"""
        self._state, data = await PhoneLoginApi.send_authcode(self.phone, self.area_code)
        if self._state == PhoneLoginEvents.CAPTCHA:
            self.auth_url = data
        elif self._state == PhoneLoginEvents.OTHER:
            self.error_msg = data
        return self._state

    async def authorize(self, auth_code: int) -> Credential:
        """验证码鉴权

        Args:
            auth_code: 验证码
        """
        if self.credential:
            return self.credential
        self.credential = await PhoneLoginApi.authorize(self.phone, auth_code, self.area_code)
        return self.credential
