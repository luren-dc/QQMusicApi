"""Credential 未提供 refreshkey 或为空"""

from .ApiException import ApiException


class CredentialNoRefreshkeyException(ApiException):
    """Credential 未提供 refreshkey 或为空"""

    def __init__(self):
        super().__init__("Credential 未提供 refreshkey 或为空")
