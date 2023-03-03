from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db


# @dataclass
# class Theme:
#     id: Optional[int]
#     title: str


@dataclass
class Question:
    id: Optional[int]
    title: str
    answers: list["Answer"]


@dataclass
class Answer:
    title: str



# class ThemeModel(db):
#     __tablename__ = "themes"
#     id = Column(Integer, primary_key=True)
#     title = Column(String, unique=True)
#     questions = relationship(
#         'QuestionModel', cascade='delete, merge, save-update')


class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    game_id = Column(
        Integer, ForeignKey('games.id'), nullable=False)
    answers = relationship('AnswerModel', cascade='delete, merge, save-update')


class AnswerModel(db):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    question_id = Column(
        Integer, ForeignKey('questions.id', ondelete='CASCADE'))
