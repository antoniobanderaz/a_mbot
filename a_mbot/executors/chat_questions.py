import abc
import re
import requests

import utils

execute = utils.MultiExecutor()


class ChatQuestion(abc.ABC):
    @abc.abstractmethod
    def match(self, req):
        pass

    @abc.abstractmethod
    def exec(self, req, matched):
        pass

    def try_exec(self, req, writer):
        if len(req.command) == 0:
            raise utils.ExecException

        match = self.match(req)
        if not match:
            raise utils.ExecException

        return (utils.Result(self.exec(req, match), req.username),)


@execute.append_instance()
class CurrencyQuestion(ChatQuestion):
    def match(self, req):
        match = re.search('(\d+|\d+\.\d+) доллар(ов|а)? в рублях',
                          req.command)
        if match:
            return match.groups()

    def exec(self, req, matched):
        try:
            resp = requests.get('http://api.fixer.io/latest',
                                params={'base': 'USD', 'symbols': 'RUB'})
        except requests.exceptions.ConnectionError:
            return 'server is not available' + utils.to_smile(req.command)

        if resp.ok:
            dollars = float(matched[0])
            сurrency = resp.json()['rates']['RUB']
            return f'{dollars} долларов = {dollars * сurrency:.2f} рублей'

        return 'something went wrong ' + utils.to_smile(req.command)
