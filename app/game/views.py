from aiohttp_apispec import response_schema

from app.web.app import View
from app.web.utils import json_response

from .schemes import (ChatListSchema, GameListSchema, PlayerListSchema,
                      ScoreListSchema, ScoreSchema)


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


class GameActiveListView(View):
    @response_schema(GameListSchema)
    async def get(self):
        chats = await self.store.games.list_chats()
        list_act_games = []
        for chat in chats:
            game = await self.store.games.get_active_game(chat.chat_id)
            if game:
                g = await self.store.games.active_games_api(chat.chat_id)
                list_act_games.append(g)
        return json_response(GameListSchema().dump({'games': list_act_games}))


class ScoreListView(View):
    @response_schema(ScoreListSchema)
    async def get(self):
        games = await self.store.games.list_games()
        score_list = []
        for game in games:
            score = await self.store.games.get_score_state(game.id)
            score_list.append(score)
        return json_response(ScoreListSchema().dump({'scores': score_list}))
