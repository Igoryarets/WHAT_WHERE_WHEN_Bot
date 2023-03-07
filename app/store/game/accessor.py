from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.base.base_accessor import BaseAccessor
from app.game.models import PlayerModel, Player, GameModel, Game, ChatModel, players_chats, players_games
from sqlalchemy.orm import selectinload



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


    async def create_chat(self, chat_id):
        try:
            async with self.app.database.session() as db:
                db.add(ChatModel(chat_id=chat_id))
                await db.commit()
        except IntegrityError:
            pass


    async def get_list_chat(self):
        pass


    async def create_game(self, chat_id: int, players: list[dict], questions_id: int) -> Game:
        game = GameModel(chat_id=chat_id, question_id=questions_id)
        
        async with self.app.database.session() as db:
            db.add(game)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise

            await self.add_players_to_game(players, chat_id, game.id)

        return Game(chat_id=game.chat_id, question_id=game.question_id)


    async def add_players_to_game(self, players: list[dict], chat_id: int, game_id: int):
        async with self.app.database.session() as db:
            
            # game = await db.execute(
            #     select(GameModel).where(
            #         GameModel.id == game_id
            #     )
            # )

            # chat = await db.execute(
            #     select(ChatModel).where(
            #         ChatModel.chat_id == chat_id
            #     )
            # )    
            # 

            game = await db.get(GameModel, game_id)
            chat = await db.get(ChatModel, chat_id)        

            for user_id in players:
                player = await db.get(
                    entity=PlayerModel,
                    ident=user_id['user_id'],
                    options=[
                        selectinload(PlayerModel.games),
                        selectinload(PlayerModel.chats),
                    ],
                )
                player.games.append(game)
                player.chats.append(chat)
            
            await db.commit()
    


    async def get_game_by_question_id(self, question_id):
        async with self.app.database.session() as db:
            
            try:
                game = await db.execute(
                    select(GameModel).where(
                        GameModel.question_id == question_id
                    )
                )
                (res, ) = game.first()
            except TypeError:
                return None
        return Game(game_id=res.id, question_id=res.question_id)
            
            
    async def get_list_game(self):
        pass



    
    # async def finish_game(self, game_id: int, players: list[Player]) -> None:
    #     async with self.session() as db:
    #         await db.execute(
    #             update(GameModel)
    #             .where(GameModel.id == game_id)
    #             .values(end_time=datetime.now())
    #         )
    #         for player in players:
    #             db_player: PlayerModel = await db.get(PlayerModel, player.id)
    #             db_player.balance = player.balance
    #             db.add(db_player)
    #         await db.commit()

    


