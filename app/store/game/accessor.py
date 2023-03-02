from typing import Optional

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.game.models import PlayerModel, GameModel, ChatModel


class GameAccessor(BaseAccessor):
    
    async def create_player(self):
        pass
    
    
    async def get_list_players(self):
        pass


    async def create_chat(self):
        pass


    async def get_list_chat(self):
        pass


    async def create_game(self):
        pass


    async def get_list_game(self):
        pass

    


