"""API Exception"""


class ApiException(Exception):
    """API Exception 基类"""

    def __init__(self, message: str = "出现了错误,但未说明原因") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class ResponseCodeError(ApiException):
    """API 返回响应的 code 不符合预期"""

    def __init__(
        self,
        code: int,
        data: dict,
        raw: dict,
        message: str = "API 返回的响应 code 不符合预期",
    ) -> None:
        self.code = code
        self.data = data
        self.raw = raw
        self.message = message

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class CredentialExpiredError(ResponseCodeError):
    """Credential 过期"""

    def __init__(
        self,
        data: dict,
        raw: dict,
        message: str = "凭证已过期",
    ) -> None:
        super().__init__(1000, data, raw, message)

    def __str__(self) -> str:
        return self.message


class CredentialInvalidError(ApiException):
    """Credential 无效"""

    def __init__(self, message: str = "凭证无效") -> None:
        super().__init__(message)


class LoginError(ApiException):
    """登录失败"""

    def __init__(self, message: str = "登录失败") -> None:
        super().__init__(message)


class SignInvalidError(ResponseCodeError):
    """请求签名无效"""

    def __init__(self, data: dict, message: str = "请求签名无效") -> None:
        super().__init__(2000, message=message, data=data, raw={})
