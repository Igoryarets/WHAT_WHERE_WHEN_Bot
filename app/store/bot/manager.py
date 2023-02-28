from app.base.base_accessor import BaseAccessor
import typing
import asyncio
from .base import Bot
import datetime

# from .poller import Poller
# from .worker import Worker


if typing.TYPE_CHECKING:
    from app.web.app import Application

class StartBot(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        
        # self.queue = asyncio.Queue()
        self.token = '1954880325:AAH-Ai3eahA1o6g_BZk3gdI5QeNjx3EgH5I' # create env and add token to env !!!!!!!!!!!!!!!
        self.n = 2
        # self.poller = Poller(self.token, self.queue)
        # self.worker = Worker(self.token, self.queue, self.n)
        self.bot = Bot(self.token, self.n)


    async def connect(self, app: "Application"):
        loop = asyncio.get_event_loop()
        print('bot has been started')
        try:
            loop.create_task(self.bot.start())
            loop.run_forever()
        except:
            pass
        # except KeyboardInterrupt:
        #     print("\nstopping", datetime.datetime.now())
        #     loop.run_until_complete(self.bot.stop())
        #     print('bot has been stopped', datetime.datetime.now())

    async def disconnect(self, app: "Application"):
        pass