import typing

from .views import ChatListView, GameListView, PlayerListView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):

    app.router.add_view("/game/", GameListView)
    app.router.add_view("/game/chats/", ChatListView)
    app.router.add_view("/game/players/", PlayerListView)