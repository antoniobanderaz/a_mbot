import random

from . import twitch
from . import gamefaqs
from . import metacritic
from . import tts

random.seed(1475260362)

HASH_SMILES = ['MrDestructoid', 'BibleThump', 'FailFish', 'SMOrc',
               'deIlluminati', 'WutFace', 'NotLikeThis', 'cmonBruh']

t = list(range(256))
random.shuffle(t)


def pearson_hash(s):
    h = 0
    for c in s.encode('utf-8'):
        index = h ^ c
        h = t[index]
    return h


def str_to_smile(s):
    return HASH_SMILES[pearson_hash(s) % 8]


def to_smile(obj):
    return str_to_smile(str(obj))


def tokenize(q):
    brackets = False
    curr = ''

    for s in q:
        if s == ' ' and not brackets and curr:
            yield curr
            curr = ''
        elif s == '(' and not curr:
            brackets = True
        elif s == ')' and brackets:
            curr = '(' + curr.rstrip() + ')'
            brackets = False
        elif s != ' ' or curr:
            curr += s

    if curr:
        yield curr


class ExecException(Exception):
    pass


class MultiExecutor:
    def __init__(self):
        self._executors = []

    def append_instance(self):
        def append_instance_dec(obj):
            self._executors.append(obj())
            return obj
        return append_instance_dec

    def __call__(self, req):
        for executor in self._executors:
            try:
                results = executor.try_exec(req)
            except ExecException:
                continue

            yield from results
            break
        else:
            yield Result(message='unknown command ' + to_smile(args),
                         username=req.username)
