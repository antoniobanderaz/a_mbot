import re
import abc

import attr

import config

from executors import chat_methods, chat_questions

CHAT_MSG = re.compile(r"^:(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #(\w+) :(.+)")

command_extractors = []


def command_extractor(class_):
    command_extractors.append(class_())
    return class_


def execute(irc_message):
    for extractor in command_extractors:
        result = extractor.try_extract(irc_message)
        if result:
            return result

    print(irc_message)


@attr.s
class ExtractorRequest:
    message = attr.ib()
    username = attr.ib()
    channel = attr.ib()
    command = attr.ib()


class CommandExtractor(abc.ABC):
    @abc.abstractmethod
    def match(self, irc_message):
        pass

    @abc.abstractmethod
    def execute(self, irc_message, req):
        pass

    def try_extract(self, irc_message):
        matched = self.match(irc_message)
        if matched:
            return self.execute(irc_message, matched)


@command_extractor
class PingExtr(CommandExtractor):
    def match(self, irc_message):
        match = re.search(r'^PING :(.+)$', irc_message)
        if match:
            return match.groups()

    def execute(self, irc_message, req):
        print(irc_message)
        return 'PONG :' + req[0]


@command_extractor
class BotCommandExtr(CommandExtractor):
    def match(self, irc_message):
        match = CHAT_MSG.search(irc_message)
        if match:
            username, channel, message = match.groups()
            if message[0] == ':':
                return ExtractorRequest(message, username,
                                        channel, message[1:])

    def execute(self, irc_message, req):
        print(' ' * 4 + req.username + ':', req.message)
        result = chat_methods.execute(req)

        return 'PRIVMSG #{0} :@{1.username}, {1.message}'.format(req.channel,
                                                                result)


@command_extractor
class InlineCommandExtr(CommandExtractor):
    inline_command_pattern = re.compile(r'#\{(.+)\}')

    def match(self, irc_message):
        match_message = CHAT_MSG.search(irc_message)
        if not match_message:
            return

        username, channel, message = match_message.groups()

        match_inline = self.inline_command_pattern.search(message)
        if not match_inline:
            return

        return ExtractorRequest(message, username,
                                channel, match_inline.group(1))

    def execute(self, irc_message, req):
        print(' ' * 4 + req.username + ':', req.message)

        result = chat_methods.execute(req)
        result = self.inline_command_pattern.sub(result.message, req.message)

        return 'PRIVMSG #{} :{}'.format(req.channel, result)


@command_extractor
class QuestionExtr(CommandExtractor):
    question_pattern = re.compile(r'^@' + config.bot_name + r', (.+)$')

    def match(self, irc_message):
        match_message = CHAT_MSG.search(irc_message)
        if not match_message:
            return

        username, channel, message = match_message.groups()

        match_question = self.question_pattern.search(message)
        if not match_question:
            return

        return ExtractorRequest(message, username,
                                channel, match_question.group(1))

    def execute(self, irc_message, req):
        print(' ' * 4 + req.username + ':', req.message)
        req.command = re.sub('[^\w.]+', ' ', req.command).strip()
        result = chat_questions.execute(req)
        return 'PRIVMSG #{} :@{}, {}'.format(req.channel, result.username,
                                             result.message)
