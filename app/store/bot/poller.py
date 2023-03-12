import asyncio
import logging
from asyncio import CancelledError, Task
from typing import Optional

from app.store.tg_api.tg_api import TgClient


class Poller:
    def __init__(self, token: str, queue: asyncio.Queue):       
        self.tg_client = TgClient(token)
        self.queue = queue
        self._task: Optional[Task] = None

    async def _worker(self):
        offset = -1
        while True:
            res = await self.tg_client.get_updates_in_objects(offset=offset, timeout=60)
            try:                
                for u in res.result:
                    offset = u.update_id + 1
                    logging.info(f'add to queue {u}')
                    self.queue.put_nowait(u)
            except CancelledError:
                break
            except Exception as e:
                logging.exception(f'ERROR in poller {e}')

    async def start(self):
        try:
            self._task = asyncio.create_task(self._worker()).add_done_callback(self.done_callback)
        except CancelledError:
            pass

    def done_callback(self, future: asyncio.Future):
        if future.exception():            
            logging.exception(f'error in task poller {future.exception()}')
    
    async def stop(self):
        self._task.cancel()