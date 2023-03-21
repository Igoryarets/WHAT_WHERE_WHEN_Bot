import csv
import os

from aiohttp_apispec import docs, request_schema, response_schema

from app.quiz.schemes import (DownloadQuestionsSchema, QuestionSchema,
                              QuiestionIdSchema)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class QuestionAddView(AuthRequiredMixin, View):
    @docs(
        tags=['question'],
        summary='question add',
        description='Admin authorization add question',
    )
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        data = await self.request.json()
        answer = data['answer']
        title = data['title']

        question = await self.store.quizzes.create_question(
            title=title,
            answer=answer,
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionGetById(View):
    @docs(
        tags=['question'],
        summary='question get by id',
        description='All users can view the question by id',
    )
    @request_schema(QuiestionIdSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        data = await self.request.json()
        question_id = data['question_id']
        question = await self.store.quizzes.get_question(question_id)
        return json_response(data=QuestionSchema().dump(question))


class DownloadQuestions(AuthRequiredMixin, View):
    @docs(
        tags=['question'],
        summary='26000 questions add to DB',
        description='Admin authorization add questions',
    )    
    @response_schema(DownloadQuestionsSchema)
    async def get(self):
        data_path = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)), "..", "data", "questions.csv"
        )

        with open(
            data_path, 'r', encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            await self.store.quizzes.create_questions(reader)

        return json_response(DownloadQuestionsSchema().dump(
            {'status': 'download successfull'}))
