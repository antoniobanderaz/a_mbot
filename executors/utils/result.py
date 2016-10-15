import attr

@attr.s
class Result:
    message = attr.ib(default='', convert=str)
    username = attr.ib(default=None)
