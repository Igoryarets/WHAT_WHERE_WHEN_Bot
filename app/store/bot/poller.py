import asyncio
from asyncio import Task
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
            res = await self.tg_client.get_updates_in_objects(offset=offset, timeout=30)
            for u in res.result:
                offset = u.update_id + 1
                print('!!!!!!!!!!!!!! кладем в очередь ', u)
                self.queue.put_nowait(u)
                print('!!!!!!!!!!!!!!!!!!!!очередь c положенным объектом!!!!!!!!!!!', self.queue)

    async def start(self):
        self._task = asyncio.create_task(self._worker())

    async def stop(self):
        self._task.cancel()