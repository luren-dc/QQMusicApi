class ApiException(Exception):
    """
    API 异常基类
    """

    def __init__(self, msg: str = "未知原因"):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class ArgsException(ApiException):
    """
    参数错误异常
    """

    pass


class ClientException(ApiException):
    """
    服务器连接错误异常
    """

    def __init__(self):
        super().__init__("连接到服务器时出现了问题")


class NetworkException(ApiException):
    """
    网络错误异常
    """

    def __init__(self, status: int, msg: str):
        full_msg = f"网络错误，状态码：{status} - {msg}"
        super().__init__(full_msg)
        self.status = status


class ResponseException(ApiException):
    """
    API 错误异常
    """

    def __init__(self, api: list):
        super().__init__()
        self.api = api

    def __str__(self):
        return f"接口信息：{'.'.join(self.api)}"


class CredentialCanNotRefreshException(ApiException):
    """
    Crediential 无法刷新异常
    """

    def __init__(self):
        super().__init__("Crediential 无法刷新，请检查是否缺少必要字段")


class CredentialNoMusicidException(ApiException):
    """
    Crediential 缺少 Musicid 异常
    """

    def __init__(self):
        super().__init__("Crediential 缺少 Musicid")


class CredentialNoMusickeyException(ApiException):
    """
    Crediential 缺少 Musickey 异常
    """

    def __init__(self):
        super().__init__("Crediential 缺少 Musickey")


class LoginDevicesFullException(ApiException):
    """
    登录设备已满异常
    """

    def __init__(self):
        super().__init__("登录设备已满")


class AuthcodeExpiredException(ApiException):
    """
    验证码已失效异常
    """

    def __init__(self):
        super().__init__("验证码已失效")


class AuthcodeGetFrequentlyException(ApiException):
    """
    验证码获取频繁异常
    """

    def __init__(self):
        super().__init__("验证码获取频繁")
