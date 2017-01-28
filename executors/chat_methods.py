import datetime
import random
import re
import ast
import abc
import collections
import itertools

import attr
import goslate
import pymorphy2

import utils
from utils.result import Result

random.seed()

go = goslate.Goslate()
morph = pymorphy2.MorphAnalyzer()

KAPPA_SMILES = ['Kappa', 'Keepo', 'KappaRoss', 'KappaClaus', 'KappaWealth']

execute = utils.MultiExecutor()


class MethodRequest:
    def __init__(self, extr_data):
        for attr, val in extr_data._asdict().items():
            setattr(self, attr, val)

        if not extr_data.command:
            self.method = ''
            self.args = []
        else:
            self.method, *self.args = utils.tokenize(extr_data.command)

    @property
    def args_raw(self):
        return ' '.join(self.args)


class ChatMethod(abc.ABC):
    @abc.abstractmethod
    def match(self, req):
        pass

    @abc.abstractmethod
    def exec(self, req):
        pass

    def try_exec(self, req):
        if not req.command:
            raise utils.ExecException

        req = MethodRequest(req)
        
        for i, arg in enumerate(req.args):
            if arg.startswith('@'):
                req.username = req.args.pop(i)[1:]

        if req.args:
            *args_tail, args_last = req.args
            if args_last.startswith('(') and args_last.endswith(')'):
                req.args = args_tail
                match = self.match(req)
                if not match:
                    raise utils.ExecException

                return (Result(args_last[1:-1], req.username),)

        match = self.match(req)
        if not match:
            raise utils.ExecException

        result = self.exec(req)
        if isinstance(result, collections.abc.Sequence) \
                                   and not isinstance(result, str):
            return [Result(str(message), req.username) for message in result]
        else:
            return (Result(str(result), req.username),)


def chat_method(f=None, args=0, alt_names=None):
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

    if f is None:
        return chat_method_dec
    else:
        return chat_method_dec(f)


def one_and_more_args(args_len):
    return args_len


def timeout(username, time):
    return utils.twitch.timeout(username, time), ''


@execute.append_instance()
@chat_method
def list_(req):
    return ', '.join('_'.join(re.findall('[A-Z][a-z]*',
                              i.__class__.__name__[:-6])).lower()
                     for i in execute._executors)


@execute.append_instance()
@chat_method
def time(req):
    return '{:%H:%M:%S}'.format(datetime.datetime.now())


@execute.append_instance()
@chat_method
def banme(req):
    return timeout(req.username, 10)


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
        return ast.literal_eval(req.args_raw)
    except ValueError:
        return '{too complicated BibleThump }'


@execute.append_instance()
@chat_method
def some_kappa(req):
    return random.choice(KAPPA_SMILES)


@execute.append_instance()
@chat_method(args=one_and_more_args)
def str_to_smile(req):
    command = req.args_raw  # where is method name??
    return utils.to_smile((':' + command, req.username, req.channel, command))


@execute.append_instance()
@chat_method(args=one_and_more_args)
def say(req):
    return req.args_raw


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
@chat_method(args=lambda args_len: args_len <= 1)
def gamefaqs(req):
    if req.args:
        game = req.args_raw
    else:
        game = utils.twitch.curr_game(req.channel)

    stats = utils.gamefaqs.get_stats(utils.gamefaqs.find_game_url(game))
    print(stats)
    if stats:
        return 'own - {0.own}, rate - {0.rate}, ' \
               'diff - {0.diff}, play - {0.play}'.format(stats)

    return 'something went wrong ' + utils.to_smile(req.command)


@execute.append_instance()
@chat_method(args=lambda args_len: args_len <= 1)
def metacritic(req):
    if req.args:
        game = req.args_raw
    else:
        game = utils.twitch.curr_game(req.channel)

    game_url = utils.metacritic.find_game_url(game)
    stats = utils.metacritic.get_stats(game_url)
    print(stats)
    if stats:
        return 'metacritic - {0.metacritic}, ' \
               'user score - {0.user_score}'.format(stats)

    return 'something went wrong ' + utils.to_smile(req.command)


@execute.append_instance()
@chat_method(args=1)
def isinchat(req):
    user_name = req.args[0]
    chatters = utils.twitch.get_chatters(req.channel)
    chatter_names = itertools.chain(*chatters.values())
    if user_name in chatter_names:
        return 'VoteYea'
    else:
        return 'VoteNay'


@execute.append_instance()
@chat_method(args=one_and_more_args, alt_names=['perevod', 'перевод', 'tr'])
def translate(req):
    return go.translate(req.args_raw, 'ru')


@execute.append_instance()
@chat_method(args=1, alt_names=['normal_form', 'normalize'])
def normalized(req):
    return morph.parse(req.args[0])[0].normal_form


@execute.append_instance()
@chat_method(args=1, alt_names=['разбор'])
def opencorporatag(req):
    return morph.parse(req.args[0])[0].tag.cyr_repr


@execute.append_instance()
@chat_method(args=one_and_more_args)
def tts(req):
    utils.tts.say(req.args_raw)
    return 'done'
