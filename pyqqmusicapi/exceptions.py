class QQMusicException(Exception):
    """Api错误基类"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class MusicTokenException(QQMusicException):
    pass


class ApiRequestException(QQMusicException):
    pass
