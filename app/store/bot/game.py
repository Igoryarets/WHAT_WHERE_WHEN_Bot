import logging
from asyncio import sleep, create_task
from random import randint

from sqlalchemy.orm.collections import InstrumentedList

from app.game.models import Score
from app.store import Store
from app.store.tg_api.tg_api import TgClient


class Game:
    def __init__(self, store: Store, tg_client: TgClient):
        self.store = store
        self.finish_count_round: int = 3
        self.tg_client = tg_client

    async def random_question(self) -> int:
        questions = await self.store.quizzes.list_questions()
        count_questions = len(questions)
        choice_id_questions = randint(1, count_questions - 1)
        ch_id = questions[choice_id_questions].id
        # choice_id_questions = randint(1, 26000)
        return ch_id

    async def check_uniq_question_in_game(self, question_id: int) -> bool:
        check_question = await self.store.games.get_tour_by_question_id(
            question_id)
        if check_question is None:
            return True
        return False

    async def choice_captain(self,
                             players: InstrumentedList,
                             chat_id: int) -> dict:

        if len(players) == 1:
            text = f'Капитаном на эту игру назначается {players[0].name}'
            await self.tg_client.send_message(chat_id, text)
            return players[0]
        idx = randint(0, len(players) - 1)
        text = f'Капитаном на эту игру назначается {players[idx].name}'
        await self.tg_client.send_message(chat_id, text)
        return players[idx]

    async def get_list_players(self,
                               chat_id: int,
                               players: InstrumentedList) -> bool:
        text = 'В игре сегодня участвуют:\n'
        self.list_players = {chat_id: {'numb_player': 1}}
        for player in players:
            text += f'{self.list_players[chat_id]["numb_player"]}. {player.name}\n'
            self.list_players[chat_id]["numb_player"] += 1
        await self.tg_client.send_message(chat_id, text)
        return True

    async def start_game(self,
                         chat_id: int,
                         players: InstrumentedList,
                         game_id: int) -> None:

        captain = await self.choice_captain(players, chat_id)

        await self.store.games.create_start_score_state(
            captain.name, captain.user_id, game_id)

        text = (f'Количество туров: {self.finish_count_round}.\n'
                f'Вы соревнуетесь с ботом, на каждый ответ дается 1 минута')
        await self.tg_client.send_message(chat_id, text)

    async def start_tour(self, chat_id: int, players: list[dict], id_game: int) -> None:
        state = await self.store.games.get_score_state(id_game)
        if state.timer_tour is not True:
            text = ('Дождитесь окончания тура')
            await self.tg_client.send_message(chat_id, text)
            return

        if state.get_answer is not True:
            text = ('Чтобы начать следующий тур необходимо'
                    ' ответить на предыдущий вопрос')
            await self.tg_client.send_message(chat_id, text)
            return

        if await self.finish_game(id_game, chat_id, state):
            return

        while state.choice_questions:
            random_id_quest = await self.random_question()
            check = await self.check_uniq_question_in_game(random_id_quest)
            if check is True:
                await self.store.games.create_tour(random_id_quest, id_game)
                state.choice_questions = False
                state.get_answer = False
                state.timer_tour = False
                state.start_round += 1
                await self.store.games.update_score_state_bool(
                    id_game,
                    state.choice_questions,
                    state.get_answer,
                    state.timer_tour)

                await self.get_question_from_db(
                    chat_id,
                    random_id_quest,
                    state)

                create_task(self.start_timer_tour(chat_id, id_game, players))

    async def answer(self,
                     chat_id: int,
                     user_id: int,
                     text: str,
                     id_callback_user: int,
                     game_id: int) -> bool | None:

        state = await self.store.games.get_score_state(game_id)
        if state.get_answer is True:
            return

        if state.timer_tour is not True:
            text = ('Дождитесь пока завершится время тура')
            await self.tg_client.send_message(chat_id, text)
            return

        if int(id_callback_user) != user_id:
            text = 'Отвечать должен тот игрок, которого выбрал капитан'
            await self.tg_client.send_message(chat_id, text)
            return
        else:
            answer_from_player = text.split()
            answer_quest = await self.store.games.get_answer_by_game_tour(
                game_id)

            if answer_quest.lower() in answer_from_player:
                state.score_team += 1
                text = (f'Ответ верный, поздравляем !!!\n'
                        f'Текущий счет:\n Знатоки {state.score_team}:'
                        f' Бот {state.score_bot}')
                await self.tg_client.send_message(chat_id, text)

            else:
                state.score_bot += 1
                text = (f'К сожалению вы ответили неверно,'
                        f' правильный ответ:\n {answer_quest.lower()}\n'
                        f'Текущий счет:\n Знатоки {state.score_team}:'
                        f' Бот {state.score_bot}')
                await self.tg_client.send_message(chat_id, text)

            state.get_answer = True
            state.start_round += 1
            state.choice_questions = True
            await self.store.games.update_score_state(
                                                  game_id,
                                                  state.start_round,
                                                  state.get_answer,
                                                  state.score_bot,
                                                  state.score_team,
                                                  state.choice_questions)
            return True

    async def get_question_from_db(self,
                                   chat_id: int,
                                   question_id: int,
                                   state: Score) -> None:

        question = await self.store.quizzes.get_question(question_id)
        text = (f'Раунд №{state.start_round} \n'
                f'Внимание вопрос: \n{question.question}')
        await self.tg_client.send_message(chat_id, text)

    async def captain_choice_player(self,
                                    user_id: int,
                                    id_callback_user: int,
                                    chat_id: int,
                                    game_id: int) -> None:

        state = await self.store.games.get_score_state(game_id)
        username_callback_user = await self.store.games.get_player_by_id(
            id_callback_user)

        if state.captain_id != user_id:
            text = (f'Выбрать игрока, который будет отвечать,'
                    ' должен капитан.\n'
                    f'Напоминаем, что капитаном является:\n'
                    f'{state.captain_name}\n'
                    f'id: {state.captain_id}')
            await self.tg_client.send_message(chat_id, text)
        else:
            text = f'Отвечать будет {username_callback_user.name}'
            await self.tg_client.send_message(chat_id, text)

    async def finish_game(self,
                          id_game: int,
                          chat_id: int,
                          state: Score) -> bool:
        if state.start_round == self.finish_count_round:
            text = 'Конец игры'
            await self.tg_client.send_message(chat_id, text)
            await self.get_score_game(chat_id, id_game, state)
            await self.store.games.finish_game(id_game)
            return True

    async def get_score_game(self,
                             chat_id: int,
                             id_game: int,
                             state: Score) -> None:
        if state.score_bot > state.score_team:
            text = (f'К сожалению ваша команда проиграла со счетом '
                    f'{state.score_team}:{state.score_bot}')
            await self.tg_client.send_message(chat_id, text)
            state.winner = 'Bot'
            await self.store.games.update_finish_score_state(
                id_game,
                state.start_round,
                state.score_bot,
                state.score_team,
                state.winner
            )
            return

        text = (f'Поздравляем !!!! Ваша команда одержала победу со счетом '
                f'{state.score_team}:{state.score_bot}')
        state.winner = 'Znatoki'
        await self.store.games.update_finish_score_state(
                id_game,
                state.start_round,
                state.score_bot,
                state.score_team,
                state.winner
            )
        await self.tg_client.send_message(chat_id, text)

    async def start_timer_tour(self,
                               chat_id: int,
                               id_game: int,
                               players,
                               seconds: int = 60) -> None:

        while seconds:
            await sleep(1)
            seconds -= 1
            if seconds == 30:
                check_t = await self.store.games.get_game_stop(id_game)
                if check_t:
                    return
                text = 'У вас осталось 30 секунд'
                await self.tg_client.send_message(chat_id, text)
            if seconds == 10:
                check_t = await self.store.games.get_game_stop(id_game)
                if check_t:
                    return
                text = 'У вас осталось 10 секунд'
                await self.tg_client.send_message(chat_id, text)
        # await self.finish_tour(chat_id, id_game, players)
        create_task(self.finish_tour(chat_id, id_game, players))

    async def finish_tour(self, chat_id, id_game, players):
        check_t = await self.store.games.get_game_stop(id_game)
        if check_t:
            return

        state = await self.store.games.get_score_state(id_game)
        text = (f'Капитан {state.captain_name} выберите игрока,\n'
                'который ответит на заданный вопрос')
        keyboard = {'inline_keyboard': [[{
            'text': player.name,
            'callback_data': player.user_id}]
            for player in players]}
        await self.tg_client.send_message(chat_id, text, keyboard)
        state.timer_tour = True
        await self.store.games.update_state_timer(
            id_game, state.timer_tour)

        timer_answer = await self.start_timer_answer(chat_id)
        state = await self.store.games.get_score_state(id_game)
        answer_quest = await self.store.games.get_answer_by_game_tour(id_game)
        logging.info(f'Answer from db: {answer_quest.lower()}')        

        await sleep(1.5)
        if timer_answer is True and state.get_answer is not True:
            state.get_answer = True
            state.start_round += 1
            state.choice_questions = True
            state.score_bot += 1
            state.choice_questions = True
            await self.store.games.update_score_state(
                                    id_game,
                                    state.start_round,
                                    state.get_answer,
                                    state.score_bot,
                                    state.score_team,
                                    state.choice_questions)

            text = (f'Вы не успели ответить, очко отдается боту\n'
                    f'Правильный ответ: {answer_quest.lower()}\n'
                    f'Текущий счет:\n Знатоки {state.score_team}:'
                    f' Бот {state.score_bot}')
            await self.tg_client.send_message(chat_id, text)

    async def start_timer_answer(self,
                                 chat_id: int,
                                 seconds: int = 10) -> bool:
        text = ('У Вас есть 10 секунд, чтобы написать ответ\n'
                'формат ответа /answer <ваш ответ>')
        await self.tg_client.send_message(chat_id, text)
        while seconds:
            await sleep(1)
            seconds -= 1
        return True

    async def stop_game(self, chat_id: int, id_game: int) -> None:
        text = 'Текущая игра остановлена, можно начинать новую'
        await self.tg_client.send_message(chat_id, text)
        await self.store.games.finish_game(id_game)
