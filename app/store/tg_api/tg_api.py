from typing import Optional
import aiohttp
import logging

from app.store.tg_api.dcs import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __init__(self, token: str = ''):
        self.token = token

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    async def get_me(self) -> dict:
        url = self.get_url("getMe")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 0) -> dict:
        url = self.get_url("getUpdates")
        params = {}
        if offset:
            params['offset'] = offset
        if timeout:
            params['timeout'] = timeout
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                return await resp.json()

    async def get_updates_in_objects(self, offset: Optional[int] = None, timeout: int = 0) -> GetUpdatesResponse:
        res_dict = await self.get_updates(offset=offset, timeout=timeout)
        logging.info(f'dict updates {res_dict}')       
        return GetUpdatesResponse.Schema().load(res_dict)

    async def send_message(
                            self,
                            chat_id: Optional[int] = None,
                            text: Optional[str] = None,
                            keyboard: Optional[dict] = None,
                            message_id: Optional[int] = None) -> SendMessageResponse:
        
        logging.info('work send message')

        url = self.get_url("sendMessage")
        
        if keyboard:
            payload = {
                'chat_id': chat_id,
                'text': text,
                'reply_markup': keyboard,
            }
        else:
            payload = {
                'chat_id': chat_id,
                'text': text,
            } 


        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                logging.info(f'send message {res_dict}')     
        
  