import attr

@attr.s
class Result:
    message = attr.ib(default='', convert=str)
    username = attr.ib(default=None)

    def __str__(self):
        if self.username:
            return '@{}, {}'.format(self.username, self.message)
        else:
            return self.message
