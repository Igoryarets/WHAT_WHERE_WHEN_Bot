import typing

from .views import (ChatListView, GameActiveListView, GameListView,
                    PlayerListView, ScoreListView)

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):

    app.router.add_view("/game/", GameListView)
    app.router.add_view("/game/chats/", ChatListView)
    app.router.add_view("/game/players/", PlayerListView)
    app.router.add_view("/game/active_games/", GameActiveListView)
    app.router.add_view("/game/score/", ScoreListView)
