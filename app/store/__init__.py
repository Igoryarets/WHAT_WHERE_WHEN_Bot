import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.admin.accessor import AdminAccessor
        from app.store.bot.manager import StartBot
        from app.store.game.accessor import GameAccessor
        from app.store.quiz.accessor import QuizAccessor

        self.quizzes = QuizAccessor(app)
        self.admins = AdminAccessor(app)
        self.games = GameAccessor(app)
        self.bots_manager = StartBot(app)
        # default create admin
        # app.on_startup.append(self.admins.create_admin_after_start_app)


def setup_store(app: "Application"):
    app.database = Database(app)
    # app.on_startup.append(app.database.create_db)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
