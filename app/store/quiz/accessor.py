from typing import Optional

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.quiz.models import Question, QuestionModel


class QuizAccessor(BaseAccessor):

    async def create_question(
        self, question: str, answer: str
    ) -> Question:

        async with self.app.database.session() as db:
            question = QuestionModel(
                question=question,
                answer=answer,
            )

            db.add(question)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise

        return Question(
                        id=question.id,
                        title=question.question,
                        answer=answer,
            )

    async def create_questions(self, reader):
        async with self.app.database.session() as db:
            questions = []
            for r in reader:
                question = QuestionModel(
                    question=r['question'], answer=r['answer'])
                questions.append(question)

            db.add_all(questions)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise

    async def get_question(self, question_id: int) -> Question | None:
        async with self.app.database.session() as db:
            question = await db.execute(
                select(QuestionModel).where(
                    QuestionModel.id == question_id))
            try:
                (res, ) = question.first()
                return Question(
                                id=res.id,
                                question=res.question,
                                answer=res.answer)
            except TypeError:
                return None

    async def list_questions(self) -> list[Question]:
        async with self.app.database.session() as db:
            query = select(QuestionModel)
            res = (await db.scalars(query)).all()
            list_questions = []

            for question in res:
                list_questions.append(
                    Question(
                        id=question.id,
                        question=question.question,
                        answer=question.answer,
                    )
                )
            return list_questions
