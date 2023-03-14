# import logging
from app.game.models import Player
from app.store import Store
from app.store.bot.game import Game
from app.store.tg_api.dcs import UpdateObj
from app.store.tg_api.tg_api import TgClient

KEYBOARD = {
    'keyboard_start': {
        'keyboard': [['/registration', '/create_game', '/start_game',
                      '/stop_game', '/start_tour', '/help', '/add']],
        'one_time_keyboard': False,
        'is_persistent': True,
        'resize_keyboard': True},
}


class HandlerCommand:
    def __init__(self, token: str, store: Store):
        self.tg_client = TgClient(token)
        self.game = Game(store, self.tg_client)
        self.store = store

    async def handler_command(self, update_object: UpdateObj):
        if update_object.callback_query:
            chat_id: int = update_object.callback_query.message.chat.id
            text: str = update_object.callback_query.message.text
            user_id: int = update_object.callback_query.from_.id
            user_name: str = update_object.callback_query.from_.first_name
        else:
            chat_id: int = update_object.message.chat.id
            text: str = update_object.message.text
            user_id: int = update_object.message.from_.id
            user_name: str = update_object.message.from_.first_name

        if text == '/start':
            global KEYBOARD
            keyboard = KEYBOARD['keyboard_start']
            await self.handler_start(chat_id, text, keyboard)
        elif text.startswith('/registration'):
            await self.handler_registration_user(user_id, user_name, chat_id)
        elif text.startswith('/start_tour'):
            await self.start_tour(chat_id)
        elif text.startswith('/start_game'):
            await self.start_game(chat_id)
        elif text.startswith('/create_game'):
            await self.create_game(chat_id)
        elif text.startswith('/stop_game'):
            await self.stop_game(chat_id)
        elif text.startswith('/help'):
            await self.help(chat_id)
        elif text.startswith('/add'):
            await self.create_team(chat_id, user_id, user_name)
        elif text.startswith('/answer'):
            await self.handler_answer(chat_id, user_id, text)
        else:
            await self.handler_inline(user_id, update_object, chat_id)

    async def handler_start(self, chat_id: int, text: str, keyboard) -> None:
        text = 'Здравствуйте, я бот для игры "Что, Где, Когда?"'
        await self.tg_client.send_message(chat_id, text, keyboard)

    async def help(self, chat_id: int) -> None:
        text = ('Алгоритм запуска и создания игры:\n'
                '1. Если Вы новый пользователь, то необходимо'
                ' зарегестрироваться: команда /registration;\n'
                '2. Чтобы начать играть необходимо создать'
                ' игровую сессию: команда /create_game;\n'
                '3. Далее необходимо создать команду игроков'
                ' "Знатоков": команда /add;\n'
                '4. Для инициализации начального состояния игры '
                '(создания раундов, вопросов, списка игроков, выбора капитана)'
                'необходимо выполнить команду: /start_game;\n'
                '5. Затем необходимо выполнить команду: /start_tour,'
                ' Вы получите вопрос, на который в течении 1-ой минуты '
                'необходимо будет ответить;\n'
                '6. Ответ ожидается в таком формате: /answer вводите'
                ' пробел и ответ;\n'
                'На ответ дается 10 секунд, если вы не успели ввести ответ'
                ' очко прибавляется боту !!!!\n'
                '7. Далее, чтобы начать новый тур вводите снова команду:'
                ' /start_tour;\n'
                '8. После всех сыгранных туров, бот выведет оканчательный'
                ' результат;\n'
                'Примечание: бот не читает чат, в чате возможно только одна'
                ' игровая сессия !!!\n'
                'Если в данном чате игра была не доиграна, и нужно начать'
                ' новую, то необходимо'
                ' выполнить команду: /stop_game\n\n\n'
                'Допустимые команды:\n'
                '/registration \n'
                '/create_game \n'
                '/start_tour\n'
                '/start_game\n'
                '/stop_game\n'
                '/help\n'
                '/add\n'
                '/answer')
        await self.tg_client.send_message(chat_id, text)

    async def handler_registration_user(self,
                                        user_id: int,
                                        user_name: str,
                                        chat_id: str) -> Player | None:

        player = await self.store.games.get_player_by_id(user_id)
        if player:
            text = f'Вы {player.name} уже зарегестрированы у нас :)'
            await self.tg_client.send_message(chat_id, text)
            return player
        else:
            player = await self.store.games.create_player(user_id, user_name)
            text = f'Регистрация прошла успешно, спасибо {player.name} :)'
            await self.tg_client.send_message(chat_id, text)
            return player

    async def create_team(self,
                          chat_id: int,
                          user_id: int,
                          user_name: str) -> None:
        player = await self.store.games.get_player_by_id(user_id)
        if not player:
            text = 'Вы должны пройти регистрацию'
            await self.tg_client.send_message(chat_id, text)
            return

        player = {chat_id: {'user_id': user_id, 'username': user_name}}

        act_game = await self.store.games.get_active_game(chat_id)
        id_act_game = act_game.id

        if not act_game:
            text = ('Необходимо сначала создать игру с '
                    'помощью команды /create_game')
            await self.tg_client.send_message(chat_id, text)
            return

        await self.store.games.add_players_to_game(
            player, chat_id, id_act_game)

        text = f'Добро пожаловать на игру {player[chat_id]["username"]} !!!'
        await self.tg_client.send_message(chat_id, text)

    async def create_game(self, chat_id: int) -> None:
        active_game_in_chat = await self.store.games.get_active_game(chat_id)
        if active_game_in_chat:
            text = ('В этом чате игровая сессия уже начата,'
                    'чтобы начать новую игру, необходимо дождаться'
                    ' оканчания текущей')
            await self.tg_client.send_message(chat_id, text)
            return
        await self.store.games.create_chat(chat_id)
        await self.store.games.create_game(chat_id)

        text = ('Игровая сессия создана, сейчас необходимо'
                ' создать команду знатоков'
                ' при помощи команды /add,'
                ' затем -> /start_game затем -> /start_tour')

        await self.tg_client.send_message(chat_id, text)

    async def start_game(self, chat_id: int) -> None:

        active_game_in_chat = await self.store.games.get_active_game_start(
            chat_id)
        if active_game_in_chat:
            text = ('В этом чате игровая сессия уже начата,'
                    'чтобы начать новую игру, необходимо'
                    ' дождаться оканчания текущей')
            await self.tg_client.send_message(chat_id, text)
            return

        act_game = await self.store.games.get_active_game(chat_id)
        id_act_game = act_game.id
        players = await self.store.games.get_players_to_game(id_act_game)

        if players.players == []:
            text = ('Чтобы начать играть, необходимо добавить'
                    ' себя в игру, нажмите /add \n'
                    'затем можно начать играть /start_tour')
            await self.tg_client.send_message(chat_id, text)
            return

        if players.players:
            await self.game.get_list_players(chat_id, players.players)
        await self.game.start_game(chat_id, players.players, id_act_game)

        await self.store.games.update_start_game(id_act_game)

    async def stop_game(self, chat_id: int) -> None:
        act_game = await self.store.games.get_active_game(chat_id)
        id_act_game = act_game.id        
        await self.game.stop_game(chat_id, id_act_game)

    async def start_tour(self, chat_id: int) -> None:
        act_game = await self.store.games.get_active_game(chat_id)
        if act_game.is_active_create_game is True:
            id_act_game = act_game.id
            players = await self.store.games.get_players_to_game(id_act_game)
            await self.game.start_tour(chat_id, players.players, id_act_game)
        else:
            text = ('Чтобы начать очередной тур, необходимо создать игру')
            await self.tg_client.send_message(chat_id, text)
            return

    async def handler_answer(self,
                             chat_id: int,
                             user_id: int,
                             text: str) -> None:
        act_game = await self.store.games.get_active_game(chat_id)
        id_act_game = act_game.id
        state = await self.store.games.get_score_state(id_act_game)
        await self.game.answer(
            chat_id, user_id, text, state.callback_id, id_act_game)

    async def handler_inline(self,
                             user_id: int,
                             update_object: UpdateObj,
                             chat_id: int) -> None:
        act_game = await self.store.games.get_active_game(chat_id)
        id_act_game = act_game.id

        id_callback_user = update_object.callback_query.data
        await self.store.games.update_state_callback(
            id_act_game, id_callback_user)
        state = await self.store.games.get_score_state(id_act_game)
        await self.game.captain_choice_player(
            user_id, state.callback_id, chat_id, id_act_game)
