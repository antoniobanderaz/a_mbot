import socket

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


print('start receiving')

for irc_message in chat_sock.get_irc_messages():
    result = extractors.execute(irc_message)
    if result:
        print('-->', result)
        chat_sock.send(result)
