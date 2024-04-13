class ApiException(Exception):
    """
    API 异常基类
    """

    def __init__(self, msg: str = "未知原因"):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class ClientException(ApiException):
    """
    服务器连接错误
    """

    def __init__(self):
        super().__init__()
        self.msg = "连接到服务器时出现了问题"


class NetworkException(ApiException):
    """
    网络错误
    """

    def __init__(self, status: int, msg: str):
        super().__init__(msg)
        self.status = status
        self.msg = f"网络错误，状态码：{status} - {msg}"

    def __str__(self):
        return self.msg


class ResponseCodeException(ApiException):
    """
    API 返回 code 错误
    """

    def __init__(self, code: int, subcode: int, api: list):
        super().__init__()
        self.msg = "API 返回 code 错误"
        self.code = code
        self.subcode = subcode
        self.api = api

    def __str__(self):
        return f"接口信息：{'.'.join(self.api)} 错误代码：{self.code} | {self.subcode}"


class CredientialCanNotRefreshException(ApiException):
    """
    Crediential 无法刷新
    """

    def __init__(self):
        super().__init__()
        self.msg = "Crediential 无法刷新，请检查是否缺少必要字段"


class CredentialNoMusicidException(ApiException):
    """
    Crediential 缺少 Musicid
    """

    def __init__(self):
        super().__init__()
        self.msg = "Crediential 缺少 Musicid"


class CredentialNoMusickeyException(ApiException):
    """
    Crediential 缺少 Musickey
    """

    def __init__(self):
        super().__init__()
        self.msg = "Crediential 缺少 Musickey"


class LoginDevicesFullException(ApiException):
    """
    登录设备已满
    """

    def __init__(self):
        super().__init__()
        self.msg = "登录设备已满"


class AuthcodeExpiredException(ApiException):
    """
    验证码已失效
    """

    def __init__(self):
        super().__init__()
        self.msg = "验证码已失效"


class AuthcodeGetFrequentlyException(ApiException):
    """
    验证码获取频繁
    """

    def __init__(self):
        super().__init__()
        self.msg = "验证码获取频繁"
