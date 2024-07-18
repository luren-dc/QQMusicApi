from .ApiException import ApiException


class LoginException(ApiException):
    def __init__(self, msg: str):
        super().__init__(msg)
