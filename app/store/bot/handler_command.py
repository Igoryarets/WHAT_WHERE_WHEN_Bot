from app.store.tg_api.tg_api import TgClient
from app.store.tg_api.dcs import UpdateObj

from app.web.app import View
import typing

COMMANDS_BOT = {
    'start': '/start',
    'registaration': '/registration',
    'help': '/help',
    'stop': '/stop,'
}


KEYBOARD = {
    'keyboard_start': {
        'keyboard': [['/registration', '/start_game',]],
        'one_time_keyboard': True,
         'resize_keyboard': True},
    
}


if typing.TYPE_CHECKING:
    from app.web.app import Application



class HandlerCommand(View):
    def __init__(self, token: str):
        self.tg_client = TgClient(token)

    async def handler_command(self, update_object: UpdateObj):
        chat_id = update_object.message.chat.id
        text = update_object.message.text
        message_id = update_object.message.message_id
        user_id = update_object.message.from_.id
        user_name = update_object.message.from_.first_name        
        
        if text == '/start':
            global KEYBOARD
            keyboard = KEYBOARD['keyboard_start']
            print('keyboard', keyboard)
            await self.handler_start(chat_id, text, keyboard)
        elif text == '/registration':
            await self.handler_registration_user(user_id, user_name, chat_id)

    async def handler_start(self, chat_id, text, keyboard):
        await self.tg_client.send_message(chat_id, text, keyboard)

    
    async def handler_registration_user(self, user_id, user_name, chat_id):
        player = await self.store.games.get_player_by_id(user_id=user_id)
        if player:
            text = 'Вы уже зарегестрированы у нас :)'
            await self.tg_client.send_message(chat_id, text)
        else:
            player = await self.store.games.create_player(user_id, user_name)
            text = f'Регистрация прошла успешно, спасибо {player.name} :)'
            await self.tg_client.send_message(chat_id, text)



    async def handler_help(self, update_object):
        pass


