from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db


@dataclass
class Question:
    id: Optional[int]
    question: str
    answer: str


class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    tours = relationship('TourGame')
