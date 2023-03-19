from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict, HTTPNotFound
from aiohttp_apispec import querystring_schema, request_schema, response_schema

from app.quiz.schemes import ListQuestionSchema, QuestionSchema, QuiestionIdSchema, DownloadQuestionsSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response
import csv
from pathlib import Path

class QuestionAddView(AuthRequiredMixin, View):
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
    @request_schema(QuiestionIdSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        data = await self.request.json()
        question_id = data['question_id']
        question = await self.store.quizzes.get_question(question_id)
        return json_response(data=QuestionSchema().dump(question))


class DownloadQuestions(AuthRequiredMixin, View):
    @response_schema(DownloadQuestionsSchema)
    async def get(self):
        BASE_DIR = Path(__file__).parent.parent
        current_dir = '\data\questions.csv'

        data_path = f'{BASE_DIR}{current_dir}'
        with open(
            data_path, 'r', encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            await self.store.quizzes.create_questions(reader)

        return json_response(DownloadQuestionsSchema().dump(
            {'status': 'download successfull'}))
