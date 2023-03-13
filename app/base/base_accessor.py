# import csv
import typing
from logging import getLogger
# from pathlib import Path

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BaseAccessor:
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app
        self.logger = getLogger("accessor")
        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app: "Application"):
        # BASE_DIR = Path(__file__).parent.parent
        # current_dir = '\data\questions.csv'

        # data_path = f'{BASE_DIR}{current_dir}'
        # with open(
        #     data_path, 'r', encoding='utf-8'
        # ) as file:
        #     reader = csv.DictReader(file)

        #     await self.app.store.quizzes.create_questions(reader)
        return

    async def disconnect(self, app: "Application"):
        return
