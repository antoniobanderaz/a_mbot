import re
import abc
import collections

import config

from executors import chat_methods, chat_questions

CHAT_MSG_PATTERN = re.compile(r"^:(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #(\w+) :(.+)")
INLINE_CMD_PATTERN = re.compile(r'#\{(.+)\}')
QUESTION_PATTERN = re.compile(r'^@' + config.bot_name + r', (.+)$')

Extracted = collections.namedtuple('Extracted', 'text username channel command')

command_executors = []


def command_executor(f):
    command_executors.append(f)
    return f


def execute(irc_message):
    for exec_func in command_executors:
        try:
            yield from exec_func(irc_message)
        except ExtractException:
            pass

    print(irc_message)


class ExtractException(Exception):
    pass


@command_executor
def ping_exec(irc_message):
    match = re.search(r'^PING :(.+)$', irc_message)
    if not match:
        raise ExtractException

    channel = match.group(1)
    print(irc_message)
    yield 'PONG :' + channel


@command_executor
def common_exec(irc_message):
    match = CHAT_MSG_PATTERN.search(irc_message)
    if not match:
        raise ExtractException

    username, channel, text = match.groups()
    if not text[0] == ':':
        raise ExtractException

    command = text[1:]

    print(' ' * 4 + username + ':', text)

    extr = Extracted(text=text, username=username,
                     channel=channel, command=command)

    for result in chat_methods.execute(extr):
        yield 'PRIVMSG #{} :{}'.format(channel, result)


@command_executor
def inline_exec(irc_message):
    match_message = CHAT_MSG_PATTERN.search(irc_message)
    if not match_message:
        raise ExtractException

    username, channel, text = match_message.groups()

    match_inline = INLINE_CMD_PATTERN.search(text)
    if not match_inline:
        raise ExtractException

    command = match_inline.group(1)

    print(' ' * 4 + username + ':', text)

    extr = Extracted(text=text, username=username,
                     channel=channel, command=command)

    for result in chat_methods.execute(extr):
        result = INLINE_CMD_PATTERN.sub(result.message, text)
        yield 'PRIVMSG #{} :{}'.format(channel, result)


@command_executor
def question_exec(irc_message):
    match_message = CHAT_MSG_PATTERN.search(irc_message)
    if not match_message:
        raise ExtractException

    username, channel, text = match_message.groups()

    match_question = QUESTION_PATTERN.search(text)
    if not match_question:
        raise ExtractException

    command = re.sub('[^\w.]+', ' ', match_question.group(1)).strip()

    print(' ' * 4 + username + ':', text)

    extr = Extracted(text=text, username=username,
                     channel=channel, command=command)

    for result in chat_questions.execute(extr):
        yield 'PRIVMSG #{} :@{}, {}'.format(channel,
                                            result.username,
                                            result.message)
