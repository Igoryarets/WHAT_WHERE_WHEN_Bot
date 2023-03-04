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
        'keyboard': [['/registration', '/start_game', '/help', '/add']],
        'one_time_keyboard': True,
         'resize_keyboard': True},
    
}


class HandlerCommand:
    def __init__(self, token: str, store: Store):
        self.tg_client = TgClient(token)
        self.game = Game(store, self.tg_client)
        self.store = store
        self.players = []


    async def handler_command(self, update_object: UpdateObj):
        chat_id = update_object.message.chat.id
        text = update_object.message.text
        # message_id = update_object.message.message_id
        user_id = update_object.message.from_.id
        user_name = update_object.message.from_.first_name        
        
        if text == '/start':
            global KEYBOARD
            keyboard = KEYBOARD['keyboard_start']
            await self.handler_start(chat_id, text, keyboard)
        elif text == '/registration':
            await self.handler_registration_user(user_id, user_name, chat_id)
        elif text == '/start_game':
            await self.start_game(chat_id, self.players)
        elif text == '/help':
            await self.help(chat_id)
        elif text == '/add':
            await self.create_team(chat_id, user_id, user_name)

    async def handler_start(self, chat_id, text, keyboard):
        text = 'Здравствуйте, я бот для игры "Что, Где, Когда?"'
        await self.tg_client.send_message(chat_id, text, keyboard)

    
    async def help(self, chat_id):
        text = 'Допустимые команды: '
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

    async def start_game(self, chat_id, players):
        await self.store.games.create_chat(chat_id)
        # await self.store.games.create_game(chat_id)
        text = f'Внимание, первый вопрос'
        await self.tg_client.send_message(chat_id, text)
        await self.game.start_game(chat_id, players)
        await self.game.start_timer(chat_id, seconds=10)    
    
    
    async def handler_help(self, update_object):
        pass




