from typing import Any


class QQMusicException(Exception):
    def __init__(self, error_code: int, message: str) -> None:
        self.error_code = error_code
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.error_code} -> {self.message}"

    def json(self) -> dict[str, Any]:
        return {"code": self.error_code, "msg": self.message}


class NumberException(QQMusicException):
    def __init__(self, message: str) -> None:
        super().__init__(400, message)


class TypeException(QQMusicException):
    def __init__(self, message: str) -> None:
        super().__init__(400, message)


class CookieException(QQMusicException):
    def __init__(self, message: str) -> None:
        super().__init__(502, message)


class RequestException(QQMusicException):
    def __init__(self, message: str) -> None:
        super().__init__(500, message)


class ParamsException(QQMusicException):
    def __init__(self, message: str) -> None:
        super().__init__(500, message)
