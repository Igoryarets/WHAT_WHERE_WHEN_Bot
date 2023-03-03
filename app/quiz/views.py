from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict, HTTPNotFound
from aiohttp_apispec import querystring_schema, request_schema, response_schema

from app.quiz.models import Answer
from app.quiz.schemes import ListQuestionSchema, QuestionSchema
                            #   ThemeIdSchema, ThemeListSchema, ThemeSchema)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


# class ThemeAddView(AuthRequiredMixin, View):
#     @request_schema(ThemeSchema)
#     @response_schema(ThemeSchema)
#     async def post(self):
#         title = (await self.request.json())["title"]
#         check_theme = await self.store.quizzes.get_theme_by_title(title=title)
#         if check_theme:
#             raise HTTPConflict

#         theme = await self.store.quizzes.create_theme(title=title)
#         return json_response(data=ThemeSchema().dump(theme))


# class ThemeListView(AuthRequiredMixin, View):
#     @response_schema(ThemeListSchema)
#     async def get(self):
#         themes = await self.store.quizzes.list_themes()
#         return json_response(data=ThemeListSchema().dump({'themes': themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        data = await self.request.json()
        # theme_id = data['theme_id']
        # theme = await self.store.quizzes.get_theme_by_id(id_=theme_id)

        answers = data['answers']
        answers_t = [Answer(title=answer['title']) for answer in answers]

        # if not theme:
        #     raise HTTPNotFound

        title = data['title']
        ex_question = await self.store.quizzes.get_question_by_title(
            title=title)

        if ex_question:
            raise HTTPConflict

        # answers = data['answers']
        # correct_answers = sum([answer['is_correct'] for answer in answers])

        # if correct_answers != 1:
        #     raise HTTPBadRequest

        question = await self.store.quizzes.create_question(
            title=title,
            answers=answers_t,
        )

        return json_response(data=QuestionSchema().dump(question))


# class QuestionListView(AuthRequiredMixin, View):
#     @querystring_schema(ThemeIdSchema)
#     @response_schema(ListQuestionSchema)
#     async def get(self):
#         theme_id = self.request.query.get('theme_id')
#         if theme_id is not None:
#             theme_id = int(theme_id)
#         questions = await self.store.quizzes.list_questions(theme_id)
#         return json_response(
#             data=ListQuestionSchema().dump({'questions': questions}))
