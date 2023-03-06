from random import randint
from app.store import Store
from app.store.tg_api.tg_api import TgClient
from asyncio import sleep

class Game:
    def __init__(self, store: Store, tg_client: TgClient):
        self.store = store
        self.finish_count_round: int = 7
        self.start_count_round: int = 1
        self.choice_questions: bool = True
        self.tg_client = tg_client
        self.callback_id_user: str = None
        self.answer_quest: str = None
        self.id_captain: int = None 
        self.name_captain: str = None
        self.score_player: int = 0
        self.score_bot: int = 0

    
    def random_question(self) -> int:
        # questions = await self.store.quizzes.list_questions()
        # count_questions = len(questions)
        # choice_id_questions = randint(1, count_questions - 1)
        choice_id_questions = randint(1, 26000)
        return choice_id_questions


    async def check_uniq_question_in_game(self, question_id: int) -> bool:
        check_question = await self.store.games.get_game_by_question_id(question_id)
        if check_question is None:
            return True
        return False

    async def choice_captain(self, players: list[dict], chat_id: int) -> dict:
        if len(players) == 1:
            text = f'Капитаном на эту игру назначается {players[0]["username"]}'
            await self.tg_client.send_message(chat_id, text)
            return players[0]
        idx = randint(0, len(players) - 1)
        text = f'Капитаном на эту игру назначается {players[idx]["username"]}'
        await self.tg_client.send_message(chat_id, text)
        return players[idx]


    async def start_game(self, chat_id: int, players: list[dict]) -> None:
        while self.choice_questions:            
            random_id_quest = self.random_question()
            check = await self.check_uniq_question_in_game(random_id_quest)
            if check is True:
                captain = await self.choice_captain(players, chat_id)
                await self.store.games.create_game(chat_id, players, random_id_quest)
                quest = await self.get_question_from_db(chat_id, random_id_quest)
                self.answer_quest = quest.answer
                print(f'!!!!!!!!!!!!{self.answer_quest}!!!!!!!!!!!!!')
                timer = await self.start_timer(chat_id)                
                
                if timer:

                    text = (f'Капитан {captain["username"]} выберите игрока,\n'
                            f'который ответит на заданный вопрос')
                    keyboard = {'inline_keyboard': [[{
                        'text': player['username'],
                        'callback_data': player['user_id']}] for player in players]}
                    
                    await self.tg_client.send_message(chat_id, text, keyboard)

                    self.id_captain = captain['user_id']
                    self.name_captain = captain['username']

                if self.finish_game(chat_id):
                    await self.get_score_game(chat_id)

                self.choice_questions = False


    async def answer(self, chat_id, user_id, text, id_callback_user):
        if int(id_callback_user) != user_id:
            text = 'Отвечать должен тот игрок, которого выбрал капитан'
            await self.tg_client.send_message(chat_id, text)
            return
        else:
            answer_from_player = text.split()            

            if self.answer_quest in answer_from_player:
                text = 'Ответ верный, поздравляем !!!'
                self.score_player += 1
                await self.tg_client.send_message(chat_id, text)
            else:
                text = f'К сожалению вы ответили неверно, правильный ответ {self.answer_quest}'
                self.score_bot
                await self.tg_client.send_message(chat_id, text)
        

    async def get_question_from_db(self, chat_id, question_id):
        if await self.finish_game(chat_id):
            return
        question = await self.store.quizzes.get_questions(question_id)
        text = (f'Раунд №{self.start_count_round} \n'
                f'Внимание вопрос: \n{question.question}')
        self.start_count_round += 1
        await self.tg_client.send_message(chat_id, text)
        return question
        

    async def captain_choice_player(self, user_id: int, id_choice_player: str, username_callback_user: str, chat_id: int):
        if self.id_captain != user_id:
            text = (f'Выбрать игрока, который будет отвечать, должен капитан.\n'
                    f'Напоминаем, что капитаном является:\n{self.name_captain}\n'
                    f'id: {self.id_captain}')
            await self.tg_client.send_message(chat_id, text)
        else:
            text = f'Отвечать будет {username_callback_user}'
            await self.tg_client.send_message(chat_id, text)


    async def finish_game(self, chat_id):
        if self.start_count_round == self.finish_count_round:
            text = 'Конец игры'
            await self.tg_client.send_message(chat_id, text)
            return True

    
    async def get_score_game(self, chat_id):
        if self.score_bot > self.score_player:
            text = (f'К сожалению ваша команда проиграла со счетом '
                    f'{self.score_player}:{self.score_bot}')
            await self.tg_client.send_message(chat_id, text)
        
        text = (f'Поздравляем !!!! Ваша команда одержала победу со счетом '
                f'{self.score_player}:{self.score_bot}')
        await self.tg_client.send_message(chat_id, text)
        

    async def start_timer(self, chat_id, seconds=60):
        
        while seconds:           
            await sleep(1)
            seconds -= 1
            if seconds == 30:
                text = 'У вас осталось 30 секунд'
                await self.tg_client.send_message(chat_id, text)
            if seconds == 10:
                text = 'У вас осталось 10 секунд'
                await self.tg_client.send_message(chat_id, text)
        return True     
   