class QQMusicException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class GetQimeiFailedException(Exception):
    pass


class NotLoginedException(Exception):
    pass


class RequestException(Exception):
    pass
