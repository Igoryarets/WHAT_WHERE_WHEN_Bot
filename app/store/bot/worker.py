import asyncio
import datetime
from typing import List

from app.store.tg_api.tg_api import TgClient
from app.store.tg_api.dcs import UpdateObj


class Worker:
    def __init__(self, token: str, queue: asyncio.Queue, concurrent_workers: int):
        self.tg_client = TgClient(token)
        self.queue = queue
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []        

    async def handle_update(self, upd: UpdateObj):
        await self.tg_client.send_message(upd.message.chat.id, upd.message.text, upd.message.message_id)

    async def _worker(self):
        while True:
            upd = await self.queue.get()
            try:
                await self.handle_update(upd)
            finally:
                self.queue.task_done()

    async def start(self):
        self._tasks = [asyncio.create_task(self._worker()).add_done_callback(self.done_callback) for _ in range(self.concurrent_workers)]
        print('!!!!!!!!!!!!!!!!!!!!! задачи', self._tasks)

    def done_callback(self, future: asyncio.Future):
        if future.exception():            
            print('!!!!!!!!!!!!!!ОШИБКА future_worker!!!!!!!!!!!!', future.exception())

    async def stop(self):
        print('!!!!!!!!!!!!!!!!!остановка!!!!!!!!!!!!!!!!')
        await self.queue.join()
        for t in self._tasks:
            t.cancel()