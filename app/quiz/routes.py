import typing

from app.quiz.views import QuestionAddView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/quiz.add_question", QuestionAddView)
