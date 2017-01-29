
class Result:
    def __init__(self, message='', username=None):
        self._message = str(message)
        self._username = username

    def __str__(self):
        if self._username:
            return f'@{self._username}, {self._message}'
        else:
            return self._message

    def __bool__(self):
        return bool(self._message and self._username)
