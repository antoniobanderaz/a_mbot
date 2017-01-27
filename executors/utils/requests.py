import attr

from executors import utils


def attr_subrequest(parent_req_cls):
    def attr_subrequest_dec(cls):
        attrs = parent_req_cls.__dict__['__attrs_attrs__']
        attrs = [attr.name for attr in attrs]
        for attr_name in attrs:
            setattr(cls, attr_name, attr.ib())

        def __init__(self, req):
            for attr_name, attr_val in req.__dict__.items():
                setattr(self, attr_name, attr_val)
            self.init_attrs(req)

        cls.__init__ = __init__

        return cls

    return attr_subrequest_dec


@attr.s
class ExtractorRequest:
    message = attr.ib()
    username = attr.ib()
    channel = attr.ib()
    command = attr.ib()


@attr.s(init=False)
@attr_subrequest(ExtractorRequest)
class MethodRequest:
    method = attr.ib()
    args = attr.ib()
    args_raw = attr.ib()

    def init_attrs(self, req):
        if not req.command:
            self.method = ''
            self.args = []
        else:
            self.method, *self.args = utils.tokenize(req.command)

        self.args_raw = ' '.join(self.args)
