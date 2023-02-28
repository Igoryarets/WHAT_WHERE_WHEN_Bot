import asyncio

from .poller import Poller
from .worker import Worker


class Bot:
    def __init__(self, token: str, n: int):
        self.queue = asyncio.Queue()
        self.poller = Poller(token, self.queue)
        self.worker = Worker(token, self.queue, n)
        print('token', token)

    async def start(self):
        await self.poller.start()
        print('start poller')
        await self.worker.start()
        print('start worker')


    async def stop(self):
        await self.poller.stop()
        await self.worker.stop()