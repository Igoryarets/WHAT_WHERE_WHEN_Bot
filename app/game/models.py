from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, Table, Text, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db

# from sqlalchemy.orm import declarative_base

# db = declarative_base()


players_chats = Table(
    'players_chats',
    db.metadata,
    Column('tg_user_id', ForeignKey('players.tg_user_id'), nullable=False),
    Column('tg_chat_id', ForeignKey('chats.tg_chat_id'), nullable=False),
)

players_games = Table(
    'players_games',
    db.metadata,
    Column('tg_user_id', ForeignKey('players.tg_user_id'), nullable=False),
    Column('game_id', ForeignKey('games.id'), nullable=False),
)


class PlayerModel(db):
    __tablename__ = 'players'

    tg_user_id = Column(Integer(), primary_key=True)
    name = Column(Text(), nullable=False)
    balance = Column(Integer(), nullable=False)

    chats = relationship(
        'ChatModel', secondary=players_chats, back_populates='players'
    )
    games = relationship(
        'GameModel', secondary=players_games, back_populates='players'
    )


class ChatModel(db):
    __tablename__ = 'chats'

    tg_chat_id = Column(Integer(), primary_key=True)

    players = relationship(
        'PlayerModel', secondary=players_chats, back_populates='chats'
    )
    games = relationship('GameModel', back_populates='chat')


class GameModel(db):
    __tablename__ = 'games'

    id = Column(Integer(), primary_key=True)
    tg_chat_id = Column(ForeignKey('chats.tg_chat_id'), nullable=False)
    start_time = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    end_time = Column(TIMESTAMP(timezone=True))

    players = relationship(
        'PlayerModel', secondary=players_games, back_populates='games'
    )
    chat = relationship('ChatModel', back_populates='games')
