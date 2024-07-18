from .ApiException import ApiException


class CredentialNoRefreshkeyException(ApiException):
    def __init__(self):
        super().__init__("Credential 未提供 refreshkey 或为空")
