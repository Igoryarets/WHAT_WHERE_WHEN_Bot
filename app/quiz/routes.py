import typing

from app.quiz.views import DownloadQuestions, QuestionAddView, QuestionGetById

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/quiz.add_question", QuestionAddView)
    app.router.add_view("/quiz.get_question", QuestionGetById)
    app.router.add_view("/quiz.download_questions", DownloadQuestions)
