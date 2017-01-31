import re
import asyncio

from . import config

from . import chat
from . import extractors


def ping_check(irc_message):
    match = re.search(r'^PING :(.+)$', irc_message)
    if not match:
        return

    irc_server = match.group(1)
    print(irc_message)
    return f'PONG :{irc_server}'


class ChatSockWriter:
    def __init__(self, chat_sock):
        self._chat_sock = chat_sock

    async def write(self, text):
        await self._chat_sock.send(text)


async def main(loop=None):
    reader, writer = await asyncio.open_connection(host=config.HOST,
                                                   port=config.PORT, loop=loop)

    chat_sock = chat.ChatSocket(reader, writer, loop=loop)

    await chat_sock.send(f'PASS {config.oauth_pass}', no_timeout=True)
    await chat_sock.send(f'NICK {config.bot_name}', no_timeout=True)
    await chat_sock.send(f'JOIN #{config.channel_name}', no_timeout=True)
    await chat_sock.send('CAP REQ :twitch.tv/membership', no_timeout=True)

    sock_writer = ChatSockWriter(chat_sock)
    print('start receiving')

    async for irc_message in chat_sock.get_irc_messages():
        check = ping_check(irc_message)
        if check:
            print('-->', check)
            await chat_sock.send(check, no_timeout=True)
            continue

        for result in extractors.execute(irc_message, sock_writer):
            if not result:
                continue

            print('-->', result)
            await chat_sock.send(result)


def start_loop():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop=loop))


if __name__ == '__main__':
    start_loop()
