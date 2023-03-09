from typing import Optional
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.base.base_accessor import BaseAccessor
from app.game.models import PlayerModel, Player, GameModel, Game, ChatModel, TourGame, Tour
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
            # await self.add_player_to_game()
        return Player(
            user_id=new_player.user_id,
            name=new_player.name)


    # async def add_player_to_game(self, player, chat_id: int, game_id: int):
    #     async with self.app.database.session() as db:

    #         game = await db.get(GameModel, game_id)
    #         chat = await db.get(ChatModel, chat_id)

    #         pl = await db.get(
    #             entity=PlayerModel,
    #             ident=player['user_id'],
    #             options=[
    #                 selectinload(PlayerModel.games),
    #                 selectinload(PlayerModel.chats),
    #             ],
    #         )
    #         player.games.append(game)
    #         player.chats.append(chat)
            
    #         await db.commit()

    
    
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


    async def create_game(self, chat_id: int, players: list[dict]) -> Game:
        game = GameModel(chat_id=chat_id, is_active=True)
        
        async with self.app.database.session() as db:
            db.add(game)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise

            await self.add_players_to_game(players, chat_id, game.id)

        return Game(id=game.id, chat_id=game.chat_id, is_active=game.is_active)


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
                    ident=user_id[chat_id]['user_id'],
                    options=[
                        selectinload(PlayerModel.games),
                        selectinload(PlayerModel.chats),
                    ],
                )
                player.games.append(game)
                player.chats.append(chat)
            
            await db.commit()
    


    # async def get_game_by_question_id(self, question_id):
    #     async with self.app.database.session() as db:
            
    #         try:
    #             game = await db.execute(
    #                 select(GameModel).where(
    #                     GameModel.question_id == question_id
    #                 )
    #             )
    #             (res, ) = game.first()
    #         except TypeError:
    #             return None
    #     return Game(game_id=res.id, question_id=res.question_id)
            
            
    async def get_list_game(self):
        pass

    
    async def get_active_game(self, chat_id):
        async with self.app.database.session() as db:
            try:
                act_game = await db.execute(
                        select(GameModel).where(
                            GameModel.chat_id == chat_id,
                            GameModel.is_active == True,
                        )
                    )
                (res, ) = act_game.first()                
            except TypeError:
                return None
        return Game(id=res.id, chat_id=res.chat_id, is_active=res.is_active)

    
    async def get_tour_by_question_id(self, question_id):
        async with self.app.database.session() as db:            
            try:
                tour = await db.execute(
                    select(TourGame).where(
                        TourGame.question_id == question_id
                    )
                )
                (res, ) = tour.first()
            except TypeError:
                return None
        return Tour(id=res.id, question_id=res.question_id, game_id=res.game_id)

    
    async def create_tour(self, question_id, game_id):
        async with self.app.database.session() as db:
            new_tour = TourGame(question_id=question_id, game_id=game_id)

            db.add(new_tour)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise
        return Tour(id=new_tour.id, question_id=new_tour.question_id, game_id=new_tour.game_id)
 

    
    
    async def finish_game(self, id_game: int, ) -> None:
        async with self.app.database.session() as db:
            await db.execute(
                update(GameModel)
                .where(GameModel.id == id_game)
                .values(finish_time=datetime.now(),
                        is_active=False)
            )
            await db.commit()

    async def stop_game(self, chat_id):
        async with self.app.database.session() as db:
            await db.execute(
                update(GameModel)
                .where(GameModel.chat_id == chat_id)
                .values(finish_time=datetime.now(),
                        is_active=False)
            )
            await db.commit()

    


