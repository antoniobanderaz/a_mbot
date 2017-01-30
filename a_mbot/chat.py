import datetime
import asyncio

from . import config

SEND_TIMEOUT = 1 / config.RATE


class ChatSocket:
    def __init__(self, reader, writer, loop=None):
        self._r = reader
        self._w = writer
        self._loop = loop

        self._last_send_time = 0
        self._t = 1

    async def send(self, message, no_timeout=False):
        curr_send_time = datetime.datetime.now().timestamp()
        diff = curr_send_time - self._last_send_time

        if no_timeout:
            self._t += 1
        else:
            pause = self._t * SEND_TIMEOUT - diff
            if pause > 0:
                await asyncio.sleep(pause, loop=self._loop)
                curr_send_time += pause
            self._t = 1

        self._w.write(message.encode('utf-8') + b'\r\n')
        await self._w.drain()

        self._last_send_time = curr_send_time

    async def get_irc_messages(self):
        response = ''
        while True:
            response += (await self._r.read(1024)).decode('utf-8')
            irc_messages = response.split('\r\n')

            if not response.endswith('\r\n'):
                response = irc_messages.pop()
            else:
                response = ''

            for i in filter(None, irc_messages):
                yield i
