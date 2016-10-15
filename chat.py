import time
import datetime

import config

SEND_TIMEOUT = 1 / config.RATE


class ChatSocket:
    def __init__(self, sock):
        self._s = sock
        self._last_send_time = 0
        self._t = 1

    @property
    def sock(self):
        return self._s

    def send(self, message, no_timeout=False):
        curr_send_time = datetime.datetime.now().timestamp()
        diff = curr_send_time - self._last_send_time

        if no_timeout:
            self._t += 1
        else:
            pause = self._t * SEND_TIMEOUT - diff
            if pause > 0:
                time.sleep(pause)
                curr_send_time += pause
            self._t = 1

        self.sock.send(message.encode('utf-8') + b'\r\n')

        self._last_send_time = curr_send_time

    def get_irc_messages(self):
        response = ''
        while True:
            response += self.sock.recv(1024).decode('utf-8')
            irc_messages = response.split('\r\n')

            if not response.endswith('\r\n'):
                response = irc_messages.pop()
            else:
                response = ''

            yield from filter(None, irc_messages)
