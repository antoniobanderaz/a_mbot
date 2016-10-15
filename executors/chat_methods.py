import datetime
import random
import re
import ast
import abc
import collections
import copy

from executors.utils.result import Result
from executors import utils

random.seed()

KAPPA_SMILES = ['Kappa', 'Keepo', 'KappaRoss', 'KappaClaus', 'KappaWealth']

execute = utils.MultiExecutor()


class MethodRequest:
    def __init__(self, req):
        for attr_name, attr_val in req.__dict__.items():
            setattr(self, attr_name, attr_val)
        if not req.command:
            self.method = ''
            self.args = []
        self.method, *self.args = utils.tokenize(self.command)


class ChatMethod(abc.ABC):
    @abc.abstractmethod
    def match(self, req):
        pass

    @abc.abstractmethod
    def exec(self, req):
        pass

    def try_exec(self, req):
        if not req.command:
            return Result(username=req.username)

        req = MethodRequest(req)
        
        for i, arg in enumerate(req.args):
            if arg.startswith('@'):
                req.username = req.args.pop(i)[1:]

        if req.args:
            *args_tail, args_last = req.args
            if args_last.startswith('(') and args_last.endswith(')'):
                req_ = copy.copy(req)
                req_.args = args_tail
                match = self.match(req_)
                if match:
                    return Result(args_last[1:-1], req.username)

        match = self.match(req)
        if not match:
            return Result(username=req.username)

        result = self.exec(req)
        return Result(str(result), req.username)


def chat_method(args=0, alt_names=None):
    if alt_names is None:
        alt_names = []
    else:
        alt_names = list(alt_names)

    def chat_method_dec(f):
        nonlocal args, alt_names
        method_name = f.__name__
        if method_name.endswith('_'):
            method_name = method_name[:-1]
        alt_names.append(method_name)

        if not callable(args):
            _args = args
            args = lambda args_len: args_len == _args

        def chat_method_match(self, req):
            return req.method in alt_names and args(len(req.args))

        def chat_method_exec(self, req):
            return f(req)

        cls_name = ''.join(i.title() for i in method_name.split('_'))
        return type(cls_name + 'Method', (ChatMethod,),
                    {'match': chat_method_match, 'exec': chat_method_exec})

    return chat_method_dec


def one_and_more_args(args_len):
    return args_len


@execute.append_instance()
@chat_method()
def time(req):
    return '{:%H:%M:%S}'.format(datetime.datetime.now())


@execute.append_instance()
@chat_method()
def banme(req):
    return 'no Kappa'


@execute.append_instance()
@chat_method(args=2)
def rand(req):
    try:
        return random.randint(int(req.args[0]), int(req.args[1])) #  same seed
    except ValueError:
        pass

    return 'wrong args ' + utils.to_smile(req.command)


@execute.append_instance()
@chat_method(args=one_and_more_args)
def pick(req):
    return random.choice(req.args)


@execute.append_instance()
@chat_method(args=one_and_more_args)
def calc(req):
    try:
        return ast.literal_eval(' '.join(req.args))
    except ValueError:
        return '{too complicated BibleThump }'


@execute.append_instance()
@chat_method()
def some_kappa(req):
    return random.choice(KAPPA_SMILES)


@execute.append_instance()
@chat_method(args=one_and_more_args)
def str_to_smile(req):
    command = ' '.join(req.args)
    return utils.to_smile((':' + command, req.username, req.channel, command))


@execute.append_instance()
@chat_method(args=one_and_more_args)
def say(req):
    return ' '.join(req.args)


@execute.append_instance()
@chat_method(args=lambda args_len: args_len <= 1)
def uptime(req):
    if req.args:
        req.channel = req.args[0]
    uptime = utils.twitch.uptime(req.channel)
    if uptime:
        return str(uptime).split('.', 1)[0]

    return 'stream is offline'


@execute.append_instance()
@chat_method(args=lambda args_len: args_len <= 1)
def game(req):
    if req.args:
        req.channel = req.args[0]
    game = utils.twitch.curr_game(req.channel)
    if game:
        return game

    return 'stream is offline'


@execute.append_instance()
@chat_method(args=one_and_more_args)
def gamefaqs(req):
    if req.args:
        game = ' '.join(req.args)
    else:
        game = utils.twitch.curr_game(req.channel)

    stats = utils.gamefaqs.get_stats(utils.gamefaqs.find_game_url(game))
    print(stats)
    if stats:
        return 'own - {0.own}, rate - {0.rate}, ' \
               'diff - {0.diff}, play - {0.play}'.format(stats)

    return 'something went wrong ' + utils.to_smile(req.command)


@execute.append_instance()
@chat_method(args=one_and_more_args)
def metacritic(req):
    if req.args:
        game = ' '.join(req.args)
    else:
        game = utils.twitch.curr_game(req.channel)

    game_url = utils.metacritic.find_game_url(game)
    stats = utils.metacritic.get_stats(game_url)
    print(stats)
    if stats:
        return 'metacritic - {0.metacritic}, ' \
               'user score - {0.user_score}'.format(stats)

    return 'something went wrong ' + utils.to_smile(req.command)
