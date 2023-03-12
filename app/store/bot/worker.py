import asyncio
import datetime
import logging
from asyncio import CancelledError
from typing import List

from app.store import Store
from app.store.bot.handler_command import HandlerCommand
from app.store.tg_api.dcs import UpdateObj


class Worker:
    def __init__(
                self,
                token: str,
                queue: asyncio.Queue,
                concurrent_workers: int,
                store: Store):

        
        self.queue = queue
        self.handler = HandlerCommand(token, store)
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []


    async def handle_update(self, update_object: UpdateObj):
            await self.handler.handler_command(update_object) 


    async def _worker(self):
        while True:
            update_object = await self.queue.get()
            try:
                await self.handle_update(update_object)
            except CancelledError:
                break
            except Exception as e:
                logging.exception(f'ERROR in worker {e}')
            finally:
                self.queue.task_done()

    async def start(self):
        try:
            self._tasks = [asyncio.create_task(self._worker()).add_done_callback(self.done_callback) for _ in range(self.concurrent_workers)]
        except CancelledError:
            pass

    def done_callback(self, future: asyncio.Future):
        if future.exception():
            logging.exception(future.exception())

    async def stop(self):
        await self.queue.join()
        for t in self._tasks:
            t.cancel()