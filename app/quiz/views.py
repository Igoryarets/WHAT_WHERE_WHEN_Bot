from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict, HTTPNotFound
from aiohttp_apispec import querystring_schema, request_schema, response_schema

from app.quiz.schemes import ListQuestionSchema, QuestionSchema, QuiestionIdSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


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
