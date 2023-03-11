from typing import Optional
from datetime import datetime

from sqlalchemy import select, update, desc
from sqlalchemy.exc import IntegrityError
from app.quiz.models import QuestionModel
from app.base.base_accessor import BaseAccessor
from app.game.models import PlayerModel, Player, GameModel, Game, ChatModel, TourGame, Tour, ScoreModel, Score
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
    
    async def create_game(self, chat_id: int) -> Game:
        game = GameModel(chat_id=chat_id,
                         is_active_create_game=True,
                         is_active_start_game=False)
        
        async with self.app.database.session() as db:
            db.add(game)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise            

        return Game(id=game.id,
                    chat_id=game.chat_id,
                    is_active_create_game=game.is_active_create_game,
                    is_active_start_game=game.is_active_start_game)

    
    async def add_players_to_game(self, player: dict, chat_id: int, game_id: int):
        async with self.app.database.session() as db:
            
            game = await db.get(GameModel, game_id)
            chat = await db.get(ChatModel, chat_id)      

            player = await db.get(
                entity=PlayerModel,

                ident=player[chat_id]['user_id'],
                options=[
                    selectinload(PlayerModel.games),
                    selectinload(PlayerModel.chats),
                ],
            )
            player.games.append(game)
            player.chats.append(chat)
               
            await db.commit()

    async def get_players_to_game(self, game_id: int):
        async with self.app.database.session() as db:
            players = await db.get(GameModel, game_id, [selectinload(GameModel.players)])
            return players               
             
            
    async def get_list_game(self):
        pass

    
    async def get_active_game(self, chat_id):
        async with self.app.database.session() as db:
            try:
                act_game = await db.execute(
                        select(GameModel).where(
                            GameModel.chat_id == chat_id,
                            GameModel.is_active_create_game == True,
                        )
                    )
                (res, ) = act_game.first()                
            except TypeError:
                return None
        return Game(id=res.id,
                    chat_id=res.chat_id,
                    is_active_create_game=res.is_active_create_game,
                    is_active_start_game=res.is_active_start_game)


    async def get_active_game_start(self, chat_id):
        async with self.app.database.session() as db:
            try:
                act_game = await db.execute(
                        select(GameModel).where(
                            GameModel.chat_id == chat_id,
                            GameModel.is_active_start_game == True,
                        )
                    )
                (res, ) = act_game.first()                
            except TypeError:
                return None
        return Game(id=res.id,
                    chat_id=res.chat_id,
                    is_active_create_game=res.is_active_create_game,
                    is_active_start_game=res.is_active_start_game)

    
    async def get_answer_by_game_tour(self, game_id):
        async with self.app.database.session() as db:
            try:
                query = await db.execute(
                    select(QuestionModel).join(
                        TourGame).where(
                            TourGame.game_id == game_id).order_by(desc(TourGame.id))
                )
                
                (res, ) = query.first()

            except TypeError:
                return None
        return res.answer



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
                        is_active_create_game=False,
                        is_active_start_game=False)
            )
            await db.commit()

    async def update_start_game(self, id_game):
        async with self.app.database.session() as db:
            await db.execute(
                update(GameModel)
                .where(GameModel.id == id_game)
                .values(is_active_start_game=True)
            )
            await db.commit()

    async def stop_game(self, chat_id):
        async with self.app.database.session() as db:
            await db.execute(
                update(GameModel)
                .where(GameModel.chat_id == chat_id)
                .values(finish_time=datetime.now(),
                        is_active_create_game=False,
                        is_active_start_game=False)
            )
            await db.commit()


    async def create_start_score_state(
                                self,
                                captain_name,
                                captain_id,
                                game_id,
                                start_round=0,
                                finish_round=3,
                                choice_questions=True,
                                timer_tour=True,
                                get_answer=True,
                                score_bot=0,
                                score_team=0,
                                winner= ''
                                ):
        async with self.app.database.session() as db:
            start_state = ScoreModel(
                captain_name=captain_name,
                captain_id=captain_id,
                game_id=game_id,
                start_round=start_round,
                finish_round=finish_round,
                choice_questions=choice_questions,
                timer_tour=timer_tour,
                get_answer=get_answer,
                score_bot=score_bot,
                score_team=score_team,
                winner=winner
            )
            db.add(start_state)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise
            return Score(
                captain_name=start_state.captain_name,
                captain_id=start_state.captain_id,
                game_id=start_state.game_id,
                start_round=start_state.start_round,
                finish_round=start_state.finish_round,
                choice_questions=start_state.choice_questions,
                timer_tour=start_state.timer_tour,
                get_answer=start_state.get_answer,
                score_bot=start_state.score_bot,
                score_team=start_state.score_team,
                winner=start_state.winner
            )


    async def update_score_state(
                            self,
                            game_id,
                            start_round,
                            # finish_round,
                            # choice_questions,
                            # timer_tour,
                            get_answer,
                            score_bot,
                            score_team,
                            choice_questions):
                            # winner):
        async with self.app.database.session() as db:
            await db.execute(
                update(ScoreModel)
                .where(ScoreModel.game_id == game_id)
                .values(start_round=start_round,
                        # finish_round=finish_round,
                        # choice_questions=choice_questions,
                        # timer_tour=timer_tour,
                        get_answer=get_answer,
                        score_bot=score_bot,
                        score_team=score_team,
                        choice_questions=choice_questions)
                        # winner=winner)
            )
            await db.commit()


    async def update_finish_score_state(
                            self,
                            game_id,
                            start_round,
                            # finish_round,
                            # choice_questions,
                            # timer_tour,
                            # get_answer,
                            score_bot,
                            score_team,
                            # choice_questions,
                            winner):
        async with self.app.database.session() as db:
            await db.execute(
                update(ScoreModel)
                .where(ScoreModel.game_id == game_id)
                .values(start_round=start_round,
                        # finish_round=finish_round,
                        # choice_questions=choice_questions,
                        # timer_tour=timer_tour,
                        # get_answer=get_answer,
                        score_bot=score_bot,
                        score_team=score_team,
                        # choice_questions=choice_questions,
                        winner=winner)
            )
            await db.commit()

    async def update_score_state_bool(self, game_id, choice_questions, get_answer, timer_tour):
        async with self.app.database.session() as db:
            await db.execute(
                update(ScoreModel)
                .where(ScoreModel.game_id == game_id)
                .values(                        
                        choice_questions=choice_questions,
                        timer_tour=timer_tour,
                        get_answer=get_answer)

            )
            await db.commit()


    async def update_state_timer(self, game_id, timer_tour):
        async with self.app.database.session() as db:
            await db.execute(
                update(ScoreModel)
                .where(ScoreModel.game_id == game_id)
                .values(timer_tour=timer_tour)

            )
            await db.commit()


    async def get_score_state(self, game_id):
        async with self.app.database.session() as db:
            try:
                score_state = await db.execute(
                    select(ScoreModel).where(
                        ScoreModel.game_id == game_id
                    )
                )
                (res, ) = score_state.first()
            except TypeError:
                return None
        return Score(
                captain_name=res.captain_name,
                captain_id=res.captain_id,
                game_id=res.game_id,
                start_round=res.start_round,
                finish_round=res.finish_round,
                choice_questions=res.choice_questions,
                timer_tour=res.timer_tour,
                get_answer=res.get_answer,
                score_bot=res.score_bot,
                score_team=res.score_team,
                winner=res.winner
            )
        


    


