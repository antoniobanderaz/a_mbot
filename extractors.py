import re
import collections

import config

from executors import chat_methods, chat_questions

msg_pattern = r"^:(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #(\w+) :(.+)"
CHAT_MSG_PATTERN = re.compile(msg_pattern)
INLINE_CMD_PATTERN = re.compile(r'#\{(.+)\}')
QUESTION_PATTERN = re.compile(r'^@' + config.bot_name + r', (.+)$')

Extracted = collections.namedtuple('Extracted',
                                   'text username channel command')


class ChatMethodWriter:
    def __init__(self, sock_writer):
        self._sock_writer = sock_writer

    async def write(self, channel, result, username=None):
        if username:
            data = 'PRIVMSG #{} :@{}, {}'.format(channel, username, result)
        else:
            data = 'PRIVMSG #{} :{}'.format(channel, result)

        await self._sock_writer.write(data)


command_executors = []


def command_executor(f):
    command_executors.append(f)
    return f


def execute(irc_message, writer):
    method_writer = ChatMethodWriter(writer)
    for exec_func in command_executors:
        try:
            yield from exec_func(irc_message, method_writer)
            break
        except ExtractException:
            pass
    else:
        print(irc_message)


class ExtractException(Exception):
    pass


@command_executor
def common_exec(irc_message, writer):
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

    for result in chat_methods.execute(extr, writer):
        yield 'PRIVMSG #{} :{}'.format(channel, result)


@command_executor
def inline_exec(irc_message, writer):
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

    for result in chat_methods.execute(extr, writer):
        result = INLINE_CMD_PATTERN.sub(result.message, text)
        yield 'PRIVMSG #{} :{}'.format(channel, result)


@command_executor
def question_exec(irc_message, writer):
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

    for result in chat_questions.execute(extr, writer):
        yield 'PRIVMSG #{} :{}'.format(channel, result)
