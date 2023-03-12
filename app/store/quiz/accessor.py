from typing import Optional

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.quiz.models import Question, QuestionModel

                            #  Theme, ThemeModel)


class QuizAccessor(BaseAccessor):
    # async def create_theme(self, title: str) -> Theme:
    #     theme = ThemeModel(title=title)
    #     async with self.app.database.session() as db:
    #         db.add(theme)

    #         await db.commit()
    #         return Theme(id=theme.id, title=theme.title)

    # async def get_theme_by_title(self, title: str) -> Optional[Theme]:
    #     async with self.app.database.session() as db:
    #         theme = await db.execute(
    #             select(ThemeModel).where(
    #                 ThemeModel.title == title))
    #         try:
    #             (res, ) = theme.first()
    #             return Theme(id=res.id, title=res.title)
    #         except TypeError:
    #             return None

    # async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
    #     async with self.app.database.session() as db:

    #         theme = await db.execute(
    #             select(ThemeModel).where(
    #                 ThemeModel.id == id_))
    #         try:
    #             (res, ) = theme.first()
    #             return Theme(id=res.id, title=res.title)
    #         except TypeError:
    #             return None

    # async def list_themes(self) -> list[Theme]:
    #     async with self.app.database.session() as db:
    #         query = select(ThemeModel)
    #         themes = (await db.scalars(query)).all()
    #         return themes

    # async def create_answers(
    #     self, question_id: int, answer: str
    # ) -> list[Answer]:

    #     async with self.app.database.session() as db:

    #         answer_list = []
    #         for answer in answers:
    #             answer_list.append(
    #                 AnswerModel(
    #                     title=answer.title,
    #                     question_id=question_id
    #                 )
    #             )

            # db.add_all(answer_list)
            # try:
            #     await db.commit()
            # except Exception:
            #     await db.rollback()
            #     raise

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
        

    async def get_questions(self, question_id):
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


    async def get_answer(self, answer):
        async with self.app.database.session() as db:
            answer = await db.execute(
                select(QuestionModel).where(
                    QuestionModel.answer == answer))
            try:
                (res, ) = answer.first()
                return Question(
                                id=res.id,
                                question=res.question,
                                answer=res.answer)
            
            
            except TypeError:
                return None

    # async def get_answers(self, question_id: int):
    #     async with self.app.database.session() as db:
    #         query = await db.execute(
    #             select(AnswerModel).where(
    #                 AnswerModel.question_id == question_id))
    #         answers = query.all()
    #         list_answer = []
    #         for answer in answers:
    #             list_answer.append(Answer(
    #                 title=answer[0].title,
    #                 # is_correct=answer[0].is_correct
    #             ))
    #         return list_answer





    # async def get_question_by_title(self, title: str) -> Optional[Question]:
    #     async with self.app.database.session() as db:
    #         question = await db.execute(
    #             select(QuestionModel).where(
    #                 QuestionModel.title == title))
    #         try:
    #             (res, ) = question.first()
    #             return Question(
    #                             id=res.id,
    #                             title=res.title,
    #                             theme_id=res.theme_id,
    #                             answers=await self.get_answers(res.id))
    #         except TypeError:
    #             return None

    async def list_questions(self) -> list[Question]:
        async with self.app.database.session() as db:
            query = select(QuestionModel)
            res = (await db.scalars(query)).all()
            list_questions = []

            for question in res:
                list_questions.append(
                    Question(
                        id=question.id,
                        title=question.title,
                        answers=await self.get_answers(question.id)
                    )
                )
            return list_questions
