from aiohttp_apispec import request_schema, response_schema

from app.web.app import View
from app.web.utils import json_response

from .schemes import ChatListSchema, GameListSchema, PlayerListSchema


class ChatListView(View):
    @response_schema(ChatListSchema)
    async def get(self):
        chats = await self.store.games.list_chats()
        return json_response(ChatListSchema().dump({'chats': chats}))


class GameListView(View):
    @response_schema(GameListSchema)
    async def get(self):
        games = await self.store.games.list_games()
        return json_response(GameListSchema().dump({'games': games}))


class PlayerListView(View):
    @response_schema(PlayerListSchema)
    async def get(self):
        players = await self.store.games.list_players()
        return json_response(PlayerListSchema().dump({'players': players}))
