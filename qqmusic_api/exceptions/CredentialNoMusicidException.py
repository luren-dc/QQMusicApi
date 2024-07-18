from .ApiException import ApiException


class CredentialNoMusicidException(ApiException):
    def __init__(self):
        super().__init__("Credential 未提供 musicid 或为空")
