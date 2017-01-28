import socket
import re

import config

import chat
import extractors

s = socket.socket()
s.connect((config.HOST, config.PORT))

chat_sock = chat.ChatSocket(s)

chat_sock.send('PASS {}'.format(config.oauth_pass), no_timeout=True)
chat_sock.send('NICK {}'.format(config.bot_name), no_timeout=True)
chat_sock.send('JOIN #{}'.format(config.channel_name), no_timeout=True)
chat_sock.send('CAP REQ :twitch.tv/membership', no_timeout=True)


def ping_check(irc_message):
    match = re.search(r'^PING :(.+)$', irc_message)
    if not match:
        return

    irc_server = match.group(1)
    print(irc_message)
    return 'PONG :' + irc_server

print('start receiving')

for irc_message in chat_sock.get_irc_messages():
    check = ping_check(irc_message)
    if check:
        print('-->', check)
        chat_sock.send(check, no_timeout=True)
        continue

    for result in extractors.execute(irc_message):
        if not result:
            continue

        print('-->', result)
        chat_sock.send(result)
