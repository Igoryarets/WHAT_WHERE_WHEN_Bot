from random import randint
from app.store import Store
from app.store.tg_api.tg_api import TgClient
from asyncio import sleep

class Game:
    def __init__(self, store: Store, tg_client: TgClient):
        self.store = store
        self.finish_count_round: int = 3
        self.start_count_round: dict = {}
        self.list_players: dict = {}
        self.choice_questions: dict = {}
        self.timer_tour: dict = {}
        self.tg_client = tg_client
        # self.callback_id_user: str = None
        self.answer_quest: str = None
        # self.id_captain: int = None 
        # self.name_captain: str = None
        self.score_team: dict = {}
        self.score_bot: dict = {}
        self.capitans: dict = {}
        self.get_answer: dict = {}


    
    def random_question(self) -> int:
        # questions = await self.store.quizzes.list_questions()
        # count_questions = len(questions)
        # choice_id_questions = randint(1, count_questions - 1)
        choice_id_questions = randint(1, 26000)
        return choice_id_questions


    async def check_uniq_question_in_game(self, question_id: int) -> bool:
        check_question = await self.store.games.get_tour_by_question_id(question_id)
        if check_question is None:
            return True
        return False

    async def choice_captain(self, players: list[dict], chat_id: int) -> dict:

        if len(players) == 1:
            text = f'Капитаном на эту игру назначается {players[0][chat_id]["username"]}'
            await self.tg_client.send_message(chat_id, text)
            return players[0][chat_id]
        idx = randint(0, len(players) - 1)
        text = f'Капитаном на эту игру назначается {players[idx][chat_id]["username"]}'
        await self.tg_client.send_message(chat_id, text)
        return players[idx][chat_id]


    async def get_list_players(self, chat_id, players):        
        text = 'В игре сегодня участвуют:\n'
        self.list_players = {chat_id: {'numb_player': 1}}
        for player in players:
            text += f'{self.list_players[chat_id]["numb_player"]}. {player[chat_id]["username"]}\n'
            self.list_players[chat_id]["numb_player"] += 1
        await self.tg_client.send_message(chat_id, text)        
        return True

    
    async def start_game(self, chat_id, players):

        captain = await self.choice_captain(players, chat_id)

        self.capitans[chat_id] = {
                                  'username': captain['username'],
                                  'user_id': captain['user_id']                                 
                                 }
        self.start_count_round = {chat_id: {'start_count_round': 0}}
        self.choice_questions = {chat_id: {'choice_questions': True}}
        self.timer_tour = {chat_id: {'timer': True}}
        self.score_bot = {chat_id: {'score_bot': 0}}
        self.score_team = {chat_id: {'score_team': 0}}
        self.get_answer = {chat_id: {'answer': True}}

        text = (f'Количество туров: {self.finish_count_round}.\n'
                f'Вы соревнуетесь с ботом, на каждый ответ дается 1 минута')
        await self.tg_client.send_message(chat_id, text)
        


    async def start_tour(self, chat_id: int, players: list[dict], id_game: int) -> None:
        
        if self.timer_tour[chat_id]['timer'] is not True:
            text = (f'Дождитесь окончания тура')
            await self.tg_client.send_message(chat_id, text)
            return

        if self.get_answer[chat_id]['answer'] is not True:
            text = (f'Чтобы начать следующий тур необходимо ответить на предыдущий вопрос')
            await self.tg_client.send_message(chat_id, text)
            return

        if await self.finish_game(id_game, chat_id):            
            return

        while self.choice_questions[chat_id]['choice_questions']: 
                   
            random_id_quest = self.random_question()
            check = await self.check_uniq_question_in_game(random_id_quest)
            if check is True:
                await self.store.games.create_tour(random_id_quest, id_game)
                self.choice_questions[chat_id]['choice_questions'] = False         
                self.get_answer[chat_id]['answer'] = False
                self.start_count_round[chat_id]['start_count_round'] += 1
                quest = await self.get_question_from_db(chat_id, random_id_quest)
                self.answer_quest = quest.answer
                print(f'!!!!!!!!!!!!!!!{self.answer_quest}!!!!!!!!!!!!!!!!!!!!')                
                timer = await self.start_timer_tour(chat_id)                
                self.timer_tour[chat_id]['timer'] = False
                if timer:
                    text = (f'Капитан {self.capitans[chat_id]["username"]} выберите игрока,\n'
                                        f'который ответит на заданный вопрос')
                    keyboard = {'inline_keyboard': [[{
                        'text': player[chat_id]['username'],
                        'callback_data': player[chat_id]['user_id']}] for player in players]}
                    
                    await self.tg_client.send_message(chat_id, text, keyboard)
                    self.timer_tour[chat_id]['timer'] = True                    
                # await self.finish_game(id_game, chat_id)
        self.choice_questions[chat_id]['choice_questions'] = True           
              

    async def answer(self, chat_id, user_id, text, id_callback_user):
        self.get_answer[chat_id]['answer'] = True
        if int(id_callback_user) != user_id:
            text = 'Отвечать должен тот игрок, которого выбрал капитан'
            await self.tg_client.send_message(chat_id, text)
            return
        else:
            answer_from_player = text.split()            

            if self.answer_quest in answer_from_player:                
                self.score_team[chat_id]['score_team'] += 1
                text = (f'Ответ верный, поздравляем !!!\n'
                        f'Текущий счет {self.score_team[chat_id]["score_team"]}:{self.score_bot[chat_id]["score_bot"]}')
                await self.tg_client.send_message(chat_id, text)
                return True
            else:               
                self.score_bot[chat_id]['score_bot'] += 1
                text = (f'К сожалению вы ответили неверно, правильный ответ {self.answer_quest}'
                        f'Текущий счет {self.score_team[chat_id]["score_team"]}:{self.score_bot[chat_id]["score_bot"]}')
                await self.tg_client.send_message(chat_id, text)
                return True
        

    async def get_question_from_db(self, chat_id, question_id):

        question = await self.store.quizzes.get_questions(question_id)
        text = (f'Раунд №{self.start_count_round[chat_id]["start_count_round"]} \n'
                f'Внимание вопрос: \n{question.question}')
        # self.start_count_round[chat_id]['start_count_round'] += 1
        await self.tg_client.send_message(chat_id, text)
        return question
        

    async def captain_choice_player(self, user_id: int, username_callback_user: str, chat_id: int):
        if self.capitans[chat_id]['user_id'] != user_id:
            text = (f'Выбрать игрока, который будет отвечать, должен капитан.\n'
                    f'Напоминаем, что капитаном является:\n{self.capitans[chat_id]["username"]}\n'
                    f'id: {self.capitans[chat_id]["user_id"]}')
            await self.tg_client.send_message(chat_id, text)
        else:
            text = f'Отвечать будет {username_callback_user}'
            await self.tg_client.send_message(chat_id, text)


    async def finish_game(self, id_game, chat_id):
        # if self.get_answer[chat_id]['answer'] is not True:
        #     return
        if self.start_count_round[chat_id]['start_count_round'] == self.finish_count_round:
            text = 'Конец игры'
            await self.tg_client.send_message(chat_id, text)
            await self.get_score_game(chat_id)
            self.start_count_round[chat_id]['start_count_round'] = 0
            await self.store.games.finish_game(id_game)            
            return True

    
    async def get_score_game(self, chat_id):
        if self.score_bot[chat_id]['score_bot'] > self.score_team[chat_id]['score_team']:
            text = (f'К сожалению ваша команда проиграла со счетом '
                    f'{self.score_team[chat_id]["score_team"]}:{self.score_bot[chat_id]["score_bot"]}')
            await self.tg_client.send_message(chat_id, text)
            return
        
        text = (f'Поздравляем !!!! Ваша команда одержала победу со счетом '
                f'{self.score_team[chat_id]["score_team"]}:{self.score_bot[chat_id]["score_bot"]}')
        await self.tg_client.send_message(chat_id, text)
        

    async def start_timer_tour(self, chat_id, seconds=10):
        self.timer_tour = {chat_id: {'timer': False}}        
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

    async def stop_game(self, chat_id):
        # self.start_count_round[chat_id]['start_count_round'] = 0
        text = 'Текущая игра остановлена, можно начинать новую'
        await self.tg_client.send_message(chat_id, text)
        await self.store.games.stop_game(chat_id)
