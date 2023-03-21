from typing import TYPE_CHECKING, Optional

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from app.store.database import db

# from sqlalchemy.orm import declarative_base


if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None

    def create_db(self, *_: list, **__: dict) -> None:
        DATABASE_URL = ("postgresql+asyncpg://"
                        f"{self.app.config.database.user}:"
                        f"{self.app.config.database.password}@"
                        f"{self.app.config.database.host}/"
                        f"{self.app.config.database.database}")
        if not database_exists(DATABASE_URL):
            create_database(DATABASE_URL)

    async def connect(self, *_: list, **__: dict) -> None:
        DATABASE_URL = ("postgresql+asyncpg://"
                        f"{self.app.config.database.user}:"
                        f"{self.app.config.database.password}@"
                        f"{self.app.config.database.host}/"
                        f"{self.app.config.database.database}")

        self._db = db
        self._engine = create_async_engine(DATABASE_URL, echo=True)
        self.session = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False)

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self._engine:
            await self._engine.dispose()
