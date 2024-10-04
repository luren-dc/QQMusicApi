"""API Exception"""

from typing import Optional


class ApiException(Exception):
    """API Exception 基类"""

    def __init__(self, message: str = "出现了错误，但未说明原因") -> None:
        super().__init__(message)
        self.message = message


class ResponseCodeError(ApiException):
    """API 返回数据 code 错误"""

    def __init__(self, code: int, request_data: dict, raw: Optional[dict] = None) -> None:
        """初始化 ResponseCodeError

        Args:
            code: 返回的 code
            request_data: API 请求数据
            raw: 原始返回数据
        """
        self.code = code
        self.request_data = request_data
        self.raw = raw
        message = f"code: {code}, request_data: {request_data}"
        super().__init__(message)


class CredentialInvalidError(ApiException):
    """Credential 无效"""

    def __init__(self, message: str = "凭证无效") -> None:
        super().__init__(message)


class LoginError(ApiException):
    """登录失败"""

    def __init__(self, message: str = "登录失败") -> None:
        super().__init__(message)
