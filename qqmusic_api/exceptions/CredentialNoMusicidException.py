"""Credential 未提供 musicid 或为空"""

from .ApiException import ApiException


class CredentialNoMusicidException(ApiException):
    """Credential 未提供 musicid 或为空"""

    def __init__(self):
        super().__init__("Credential 未提供 musicid 或为空")
