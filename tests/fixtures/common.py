import logging
import os
from hashlib import sha256
from unittest.mock import AsyncMock

import pytest
from aiohttp.test_utils import TestClient, loop_context
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import Admin, AdminModel
from app.store import Database, Store
from app.web.app import setup_app
from app.web.config import Config
import pytest_asyncio

from sqlalchemy_utils import create_database, drop_database

from alembic import command
from alembic.config import Config as AlembicConfig

@pytest.fixture(scope="session")
def event_loop():
    with loop_context() as _loop:
        yield _loop


@pytest.fixture(autouse=True, scope="session")
def server():
    app = setup_app(
        config_path=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "config.yml"
        )
    )
    app.on_startup.clear()
    app.on_shutdown.clear()
    # app.store.vk_api = AsyncMock()
    # app.store.vk_api.send_message = AsyncMock()

    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_shutdown.append(app.database.disconnect)

    return app


# @pytest.fixture(scope="session")
# async def test_db_setup_sessionmaker(server):
#     # async with server.database.session.begin() as conn:
#     #     await conn.run_sync(server.database._db.metadata.drop_all)
#     #     await conn.run_sync(server.database._db.metadata.create_all)

#     print('WWWWWWWWWWWWWWWWWWWWWWWWWWWWW', server.database._db.metadata.tables)

#     async with server.database.session() as session:
#         for table in server.database._db.metadata.tables:
#             print('QQQQQQQQQQQQQQQQQQQQQQQQQQ', table)
#             await session.execute(text(f"CREATE TABLE {table}"))


@pytest.fixture
def store(server) -> Store:
    return server.store


@pytest.fixture
def db_session(server):
    return server.database.session


# @pytest.fixture(autouse=True, scope="function")
# async def clear_db(server):
#     yield
#     try:
#         # session = AsyncSession(server.database._engine)
#         # connection = await session.connection()
#         async with server.database.session() as session:
#             for table in server.database._db.metadata.tables:
#                 await session.execute(text(f"TRUNCATE {table} CASCADE"))
#                 await session.execute(text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1"))

#         await session.commit()
#         # await connection.close()

#     except Exception as err:
#         logging.warning(err)


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1/Tg_Bot_CHGK_test"

# @pytest.fixture(autouse=True, scope='session')
# def temp_db_create() -> None:
#     create_database(DATABASE_URL)
#     yield
#     drop_database(DATABASE_URL)




# @pytest.fixture(autouse=True)
@pytest.fixture(scope='session')
async def db(server) -> Database:
    yield
    async with server.database._engine.begin() as session:
        for table in server.database._db.metadata.tables:
            await session.execute(text(f'DROP {table} CASCADE'))
            # await session.execute(text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1"))


@pytest.fixture(scope='session')
def alembic_cfg() -> AlembicConfig:
    return AlembicConfig('alembic.ini')

@pytest.fixture(scope='session', autouse=True)
def db_migrated(alembic_cfg: AlembicConfig) -> None:
    command.upgrade(alembic_cfg, 'head')






@pytest.fixture
def config(server) -> Config:
    return server.config


@pytest.fixture(autouse=True)
def cli(aiohttp_client, event_loop, server) -> TestClient:
    return event_loop.run_until_complete(aiohttp_client(server))


@pytest.fixture
async def authed_cli(cli, config) -> TestClient:
    await cli.post(
        "/admin.login",
        data={
            "email": config.admin.email,
            "password": config.admin.password,
        },
    )
    yield cli


@pytest.fixture(autouse=True)
async def admin(cli, db_session, config: Config) -> Admin:
    new_admin = AdminModel(
        email=config.admin.email,
        password=sha256(config.admin.password.encode()).hexdigest(),
    )
    async with db_session.begin() as session:
        session.add(new_admin)

    return Admin(id=new_admin.id, email=new_admin.email)
