# from aiohttp.web_response import json_response
from app.web.utils import json_response
# from aiohttp_apispec import docs, response_schema

from app.web.app import View

# from .schemes import ChatListSchema, GameListSchema, PlayerListSchema


class ChatListView(View):
    pass


class GameListView(View):
    pass


class PlayerListView(View):
    pass
