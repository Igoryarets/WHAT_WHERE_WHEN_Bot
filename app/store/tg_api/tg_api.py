from typing import Optional

import aiohttp

from asyncio import create_task, sleep

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
        print('!!!!!!!!!!! in get_updates !!!!!!!!!!!')
        params = {}
        if offset:
            params['offset'] = offset
        if timeout:
            params['timeout'] = timeout
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                return await resp.json()

    async def get_updates_in_objects(self, offset: Optional[int] = None, timeout: int = 0) -> GetUpdatesResponse:
        print('in get_updates_in_objects')
        res_dict = await self.get_updates(offset=offset, timeout=timeout)
        print('!!!!!!!!!!!!!!!результирующий словарь: ', res_dict)
        return GetUpdatesResponse.Schema().load(res_dict)

    async def send_message(self, chat_id: int, text: str, message_id: int = None) -> SendMessageResponse:
        print('in send message')
        url = self.get_url("sendMessage")

        btn = {'keyboard': [['Привет', 'Ируха', 'Хитруха']], "one_time_keyboard": True, 'resize_keyboard': True}
        
        payload = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': btn,
        }

        if text.startswith('/start'):

            text_start = 'Здравствуйте, Вас приветствует бот-ведущий игры что где когда'
            btn = {'keyboard': [['Пуст_1', 'Пуст_2', 'Пуст_3']], "one_time_keyboard": False, 'resize_keyboard': True}

            payload = {
                'chat_id': chat_id,
                'text': text_start,
                'reply_markup': btn,
                }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    print('send')
                    res_dict = await resp.json()
                    print(res_dict)        
        
        
        
        if text.startswith('/timer') or text.startswith('Пуст_1') or text.startswith('Пуст_3'):          

            payload = {
                'chat_id': chat_id,
                'text': 'Start timer: ',
                }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    print('send')
                    res_dict = await resp.json()
                    print(res_dict)


            message_id = res_dict['result']['message_id']

            url_1 = self.get_url("editMessageText")
            seconds = 10
            create_task(self.start_timer(url_1, chat_id, seconds, message_id))

            print('message_id', message_id)
        
        
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(url, json=payload) as resp:
        #         res_dict = await resp.json()
        #         return SendMessageResponse.Schema().load(res_dict)


    async def start_timer(self, url, chat_id, seconds, message_id):

        while seconds:

            print('start_timer')

            payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f'Start timer: {seconds}',
            }
            
            await sleep(1)
            seconds -= 1

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    res_dict = await resp.json()
                    print(res_dict)


            