from typing import Optional

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.game.models import PlayerModel, Player, GameModel, ChatModel


class GameAccessor(BaseAccessor):
    
    async def create_player(self, user_id: int, name: str):
        new_player = PlayerModel(user_id=user_id, name=name)
        async with self.app.database.session() as db:
            db.add(new_player)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise
        return Player(
            user_id=new_player.user_id,
            name=new_player.name)

    async def get_player_by_id(self, user_id: int):

        print('ВВВВВВВВВВВВВВВВВВВВВВВВ')

        async with self.app.database.session() as db:
            player = await db.execute(
                select(PlayerModel).where(
                    PlayerModel.user_id == user_id
                )
            )
            try:
                (res, ) = player.first()
            except TypeError:
                return None
        return Player(user_id=res.user_id, name=res.name)
    
    
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

    

