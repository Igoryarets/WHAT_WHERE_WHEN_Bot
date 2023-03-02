from app.store import Store
from app.base.base_accessor import BaseAccessor
import typing
import asyncio
from app.store.bot.base import Bot
import datetime

# from .poller import Poller
# from .worker import Worker


if typing.TYPE_CHECKING:
    from app.web.app import Application

class StartBot(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        # self.store = Store(app: "Application")
        
        # self.queue = asyncio.Queue()
        token = '1954880325:AAH-Ai3eahA1o6g_BZk3gdI5QeNjx3EgH5I' # create env and add token to env !!!!!!!!!!!!!!!
        n = 5
        # self.poller = Poller(self.token, self.queue)
        # self.worker = Worker(self.token, self.queue, self.n)
        self.bot = Bot(token, n)


    async def connect(self, app: "Application"):
        print('bot has been started')
        
        # try:
        asyncio.create_task(self.bot.start()).add_done_callback(self.done_callback)
        # except KeyboardInterrupt:
        #     print("\nstopping", datetime.datetime.now())
        #     self.bot.stop()
        #     print('bot has been stopped', datetime.datetime.now())
    
    def done_callback(self, future: asyncio.Future):
        if future.exception():            
            print('!!!!!!!!!!!!!!ОШИБКА future!!!!!!!!!!!!', future.exception())
            

    async def disconnect(self, app: "Application"):
        pass