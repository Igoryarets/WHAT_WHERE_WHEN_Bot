import asyncio

from app.store.bot.poller import Poller
from app.store.bot.worker import Worker

# from queue import Queue

# from .context_var import queue

class Bot:
    def __init__(self, token: str, n: int):
        # queue.set(asyncio.Queue())
        # self.queue = Queue()
        self.queue = asyncio.Queue()
        self.poller = Poller(token, self.queue)
        self.worker = Worker(token, self.queue, n)

        # self.poller = Poller(token)
        # self.worker = Worker(token, n)

    async def start(self):
        await self.poller.start()
        print('start poller')
        await self.worker.start()
        print('start worker')


    async def stop(self):
        await self.poller.stop()
        await self.worker.stop()