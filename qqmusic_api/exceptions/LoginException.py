"""登录异常"""

from .ApiException import ApiException


class LoginException(ApiException):
    """登录失败"""

    def __init__(self, msg: str):
        super().__init__(msg)
