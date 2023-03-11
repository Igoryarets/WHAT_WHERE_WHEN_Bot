from datetime import datetime
from marshmallow_dataclass import dataclass

from sqlalchemy import Column, ForeignKey, Integer, Table, Text, Boolean, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

# from app.quiz.models import QuestionModel

from app.store.database.sqlalchemy_base import db



@dataclass
class Player:
    user_id: int
    name: str


@dataclass
class Game:
    id: int
    chat_id: int
    is_active: bool

@dataclass
class Score:
    captain_name: str
    captain_id: int
    game_id: int
    start_round: int
    finish_round: int
    choice_questions: bool
    timer_tour: bool
    get_answer: bool
    score_bot: int
    score_team: int
    winner: str


@dataclass
class Tour:
    id: int
    question_id: int
    game_id: bool



players_chats = Table(
    'players_chats',
    db.metadata,
    Column('user_id', ForeignKey('players.user_id'), nullable=False),
    Column('chat_id', ForeignKey('chats.chat_id'), nullable=False),
)

players_games = Table(
    'players_games',
    db.metadata,
    Column('user_id', ForeignKey('players.user_id'), nullable=False),
    Column('game_id', ForeignKey('games.id'), nullable=False),
)


class PlayerModel(db):
    __tablename__ = 'players'

    user_id = Column(Integer(), primary_key=True)
    name = Column(Text(), nullable=False)      

    chats = relationship(
        'ChatModel', secondary=players_chats, back_populates='players'
    )
    games = relationship(
        'GameModel', secondary=players_games, back_populates='players'
    )


class ChatModel(db):
    __tablename__ = 'chats'

    chat_id = Column(Integer(), primary_key=True)

    players: list['PlayerModel'] = relationship(
        'PlayerModel', secondary=players_chats, back_populates='chats'
    )
    games: list['GameModel'] = relationship('GameModel', back_populates='chats')


class GameModel(db):
    __tablename__ = 'games'

    id = Column(Integer(), primary_key=True)
    chat_id = Column(ForeignKey('chats.chat_id'), nullable=False)
    # question_id = Column(
    #     Integer, ForeignKey('questions.id'), nullable=False)
    start_time = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    finish_time = Column(TIMESTAMP(timezone=True))

    is_active = Column(Boolean, nullable=False)

    players: list['PlayerModel'] = relationship(
        'PlayerModel', secondary=players_games, back_populates='games'
    )
    chats: 'ChatModel' = relationship('ChatModel', back_populates='games')

    tours = relationship('TourGame')
    scores = relationship('ScoreModel')

    # questions = relationship('QuestionModel')


class ScoreModel(db):
    __tablename__ = 'scores'

    id = Column(Integer(), primary_key=True)
    captain_name = Column(Text(), nullable=False)
    captain_id = Column(Integer(), nullable=False)
    game_id = Column(Integer(), ForeignKey('games.id'), nullable=False)
    start_round = Column(Integer(), nullable=False)
    finish_round = Column(Integer(), nullable=False)
    choice_questions = Column(Boolean, nullable=False)
    timer_tour = Column(Boolean, nullable=False)
    get_answer = Column(Boolean, nullable=False)
    score_bot = Column(Integer(), nullable=False)
    score_team = Column(Integer(), nullable=False)
    winner = Column(Text(), nullable=False)

class TourGame(db):
    __tablename__ = 'tours'

    id = Column(Integer(), primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    question_id = Column(
        Integer, ForeignKey('questions.id'), nullable=False)

    