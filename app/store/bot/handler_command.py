from app.store.tg_api.tg_api import TgClient
from app.store.tg_api.dcs import UpdateObj

from app.store.bot.game import Game
from app.store import Store


COMMANDS_BOT = {
    'start': '/start',
    'registaration': '/registration',
    'help': '/help',
    'stop': '/stop,'
}


KEYBOARD = {
    'keyboard_start': {
        'keyboard': [['/registration', '/start_tour', '/help', '/add']],
        'one_time_keyboard': True,
         'resize_keyboard': True},
    
}


class HandlerCommand:
    def __init__(self, token: str, store: Store):
        self.tg_client = TgClient(token)
        self.game = Game(store, self.tg_client)
        self.store = store
        self.players = []
        self.id_callback_user: str =None
        self.is_list_players: bool = True
        # self.active_games: dict = {}


    async def handler_command(self, update_object: UpdateObj):

        if update_object.callback_query:
            chat_id = update_object.callback_query.message.chat.id
            text = update_object.callback_query.message.text
            user_id = update_object.callback_query.from_.id
            user_name = update_object.callback_query.from_.first_name
            id_callback_user = update_object.callback_query.message.reply_markup.inline_keyboard[0][0].callback_data
            username_callback_user = update_object.callback_query.message.reply_markup.inline_keyboard[0][0].text
        else:
            chat_id = update_object.message.chat.id
            text = update_object.message.text
            user_id = update_object.message.from_.id
            user_name = update_object.message.from_.first_name       
        
        if text == '/start':
            global KEYBOARD
            keyboard = KEYBOARD['keyboard_start']
            await self.handler_start(chat_id, text, keyboard)
        elif text.startswith('/registration'):
            await self.handler_registration_user(user_id, user_name, chat_id)
        # elif text.startswith('/start_tour'):
        #     await self.start_tour(chat_id, self.players)
        elif text.startswith('/start_game'):
            await self.start_game()
        elif text.startswith('/help'):
            await self.help(chat_id)
        elif text.startswith('/add'):
            await self.create_team(chat_id, user_id, user_name)
        elif text.startswith('/answer'):
            await self.handler_answer(chat_id, user_id, text, self.id_callback_user)
        else:
            await self.handler_inline(user_id, id_callback_user, username_callback_user, chat_id)
        

    async def handler_start(self, chat_id, text, keyboard):
        text = 'Здравствуйте, я бот для игры "Что, Где, Когда?"'
        await self.tg_client.send_message(chat_id, text, keyboard)

    
    async def help(self, chat_id):
        text = ('Допустимые команды:\n'
                '/registration \n'
                '/start_tour\n'
                '/help\n'
                '/add\n'
                '/answer')
        await self.tg_client.send_message(chat_id, text)

    
    async def handler_registration_user(self, user_id: int, user_name: str, chat_id: str):

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

    async def create_team(self, chat_id, user_id, user_name):
        player = await self.store.games.get_player_by_id(user_id)
        if not player:
            text = 'Вы должны пройти регистрацию'
            await self.tg_client.send_message(chat_id, text)
            return
        
        player = {'user_id': user_id, 'username': user_name}
        self.players.append(player)
        text = 'Добро пожаловать на игру !!!'
        await self.tg_client.send_message(chat_id, text)


    async def start_game(self, chat_id):
        if self.store.games.get_active_game(chat_id):
            text = ('В этом чате игровая сессия уже начата,'
                    'чтобы начать новую игру, необходимо дождаться оканчания текущей')
            await self.tg_client.send_message(chat_id, text)
        
        if self.players == []:
            text = (f'Чтобы начать играть, необходимо добавить себя в игру, нажмите /add \n'
                    f'затем можно начать играть /start_tour')
            await self.tg_client.send_message(chat_id, text)
            return
        
        if self.is_list_players:
            await self.game.get_list_players(chat_id, self.players)
            self.is_list_players = False

        await self.store.games.create_chat(chat_id)

        game = self.store.games.create_game(chat_id, self.players)
        id_game = game.id

        # self.active_games[chat_id] = game

        await self.game.start_game(id_game, chat_id, self.players)

    # async def start_tour(self, chat_id, players):
    #     await self.game.start_tour(chat_id, players)
    
    async def handler_answer(self, сhat_id, user_id, text, id_choice_player):
        await self.game.answer(сhat_id, user_id, text, id_choice_player)

    async def handler_inline(self, user_id, id_choice_player: str, username_callback_user: str, chat_id: int):
        self.id_callback_user = id_choice_player
        await self.game.captain_choice_player(user_id, id_choice_player, username_callback_user, chat_id)
