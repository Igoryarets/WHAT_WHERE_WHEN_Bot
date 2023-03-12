import asyncio
import logging
import typing
from asyncio import CancelledError
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.store import Store
from app.store.bot.poller import Poller
from app.store.bot.worker import Worker

# from .poller import Poller
# from .worker import Worker


if typing.TYPE_CHECKING:
    from app.web.app import Application


class StartBot(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.poller: Optional[Poller] = None
        self.worker: Optional[Worker] = None
        self.queue = asyncio.Queue()
        self.token = self.app.config.bot.token        
        self.count_concurency = 2

    async def connect(self, app: "Application"):
        logging.info('BOT START')
        self.poller = Poller(self.token, self.queue)
        self.worker = Worker(self.token, self.queue, self.count_concurency, app.store)       
        try:
            asyncio.create_task(self.start()).add_done_callback(self.done_callback)
        except CancelledError:
            pass

    async def start(self):
        await self.poller.start()
        await self.worker.start()

    def done_callback(self, future: asyncio.Future):
        if future.exception():            
            logging.exception(future.exception())
            

    async def disconnect(self, app: "Application"):
        pass