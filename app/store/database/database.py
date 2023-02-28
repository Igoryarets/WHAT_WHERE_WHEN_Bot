from typing import TYPE_CHECKING, Optional

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.store.database import db

# from sqlalchemy.orm import declarative_base


if TYPE_CHECKING:
    from app.web.app import Application

# DATABASE_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1/kts"
DATABASE_URL = "postgresql+asyncpg://kts_user:kts_pass@0.0.0.0/kts"


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        self._engine = create_async_engine(DATABASE_URL, echo=True)
        self.session = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False)

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self._engine:
            await self._engine.dispose()
