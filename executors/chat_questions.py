import abc
import re
import requests

import utils
from utils.result import Result

execute = utils.MultiExecutor()


class ChatQuestion(abc.ABC):
    @abc.abstractmethod
    def match(self, req):
        pass

    @abc.abstractmethod
    def exec(self, req, matched):
        pass

    def try_exec(self, req):
        if len(req.command) == 0:
            raise utils.ExecException

        match = self.match(req)
        if not match:
            raise utils.ExecException

        return (Result(self.exec(req, match), req.username),)


@execute.append_instance()
class CurrencyQuestion(ChatQuestion):
    def match(self, req):
        match = re.search('(\d+|\d+\.\d+) доллар(ов|а)? в рублях',
                          req.command)
        if match:
            return match.groups()

    def exec(self, req, matched):
        resp = requests.get('http://api.fixer.io/latest',
                            params={'base': 'USD', 'symbols': 'RUB'})

        if resp.ok:
            dollars = float(matched[0])
            сurrency = resp.json()['rates']['RUB']
            return '{} долларов = {:.2f} рублей'.format(dollars,
                                                        dollars * сurrency)

        return 'something went wrong ' + utils.to_smile(req.command)
