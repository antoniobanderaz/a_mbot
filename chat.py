import datetime
import asyncio

import config

SEND_TIMEOUT = 1 / config.RATE


class AsyncIrcMessagesIterator:
    def __init__(self, reader):
        self._r = reader
        self._resp = ''

    def __aiter__(self):
        return self

    async def __anext__(self):
        self._resp += (await self._r.read(1024)).decode('utf-8')
        irc_messages = self._resp.split('\r\n')

        if not self._resp.endswith('\r\n'):
            self._resp = irc_messages.pop()
        else:
            self._resp = ''

        return filter(None, irc_messages)


class AsyncFlatIterator:
    def __init__(self, aiter):
        self._aiter = aiter
        self._cur_iter = None

    def __aiter__(self):
        return self

    async def __anext__(self):
        while True:
            if self._cur_iter is None:
                self._cur_iter = iter(await self._aiter.__anext__())
            try:
                return next(self._cur_iter)
            except StopIteration:
                self._cur_iter = None


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
                await asyncio.sleep(pause)
                curr_send_time += pause
            self._t = 1

        self._w.write(message.encode('utf-8') + b'\r\n')
        await self._w.drain()

        self._last_send_time = curr_send_time

    def get_irc_messages(self):
        return AsyncFlatIterator(AsyncIrcMessagesIterator(self._r))
