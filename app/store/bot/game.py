from random import randint
from app.store import Store
from app.store.tg_api.tg_api import TgClient
from asyncio import sleep

class Game:
    def __init__(self, store: Store, tg_client: TgClient):
        self.store = store
        self.count_round: int = 3
        self.choice_questions: bool = True
        self.tg_client = tg_client

    
    async def random_question(self):
        questions = await self.store.quizzes.list_questions()
        count_questions = len(questions)
        choice_id_questions = randint(1, count_questions - 1)
        return choice_id_questions


    async def check_uniq_question_in_game(self, question_id: int) -> bool:
        check_question = await self.store.games.get_game_by_question_id(question_id)
        if check_question is None:
            return True
        return False

    async def choice_captain(self, players):
        idx = randint(0, len(players))
        return players[idx]


    async def start_game(self, chat_id, players):
        while self.choice_questions:            
            random_id_quest = await self.random_question()
            check = await self.check_uniq_question_in_game(random_id_quest)
            if check is True:
                # captain = await self.choice_captain(players)
                # await self.store.games.create_game(chat_id, random_id_quest)
                await self.store.games.create_game(chat_id, players, 34)
                # question = await self.get_question_from_db(random_id_quest)
                question = await self.get_question_from_db(34)
                text = question.title
                await self.tg_client.send_message(chat_id, text)
                await self.start_timer(chat_id)
                self.choice_questions = False
    

    async def get_question_from_db(self, question_id):
        question = await self.store.quizzes.get_questions(question_id)
        return question

    async def start_timer(self, chat_id, seconds=60):
        while seconds:           
            await sleep(1)
            seconds -= 1
            if seconds == 30:
                text = 'У вас осталось 30 секунд'
                await self.tg_client.send_message(chat_id, text)
            if seconds == 50:
                text = 'У вас осталось 10 секунд'
                await self.tg_client.send_message(chat_id, text)



# if text.startswith('/timer'):          

        #     payload = {
        #         'chat_id': chat_id,
        #         'text': 'Start timer: ',
        #         }

        #     async with aiohttp.ClientSession() as session:
        #         async with session.post(url, json=payload) as resp:
        #             print('send')
        #             res_dict = await resp.json()
        #             print(res_dict)


        #     message_id = res_dict['result']['message_id']

        #     url_1 = self.get_url("editMessageText")
        #     seconds = 10
        #     create_task(self.start_timer(url_1, chat_id, seconds, message_id))

        #     print('message_id', message_id)
        
        
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(url, json=payload) as resp:
        #         res_dict = await resp.json()
        #         return SendMessageResponse.Schema().load(res_dict)


    # async def start_timer(self, url, chat_id, seconds, message_id):

    #     while seconds:

    #         print('start_timer')

    #         payload = {
    #         'chat_id': chat_id,
    #         'message_id': message_id,
    #         'text': f'Start timer: {seconds}',
    #         }
            
    #         await sleep(1)
    #         seconds -= 1

    #         async with aiohttp.ClientSession() as session:
    #             async with session.post(url, json=payload) as resp:
    #                 res_dict = await resp.json()
    #                 print(res_dict)