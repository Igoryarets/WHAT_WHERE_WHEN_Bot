from marshmallow import Schema, fields


class ChatSchema(Schema):
    tg_chat_id = fields.Int(required=True)


class ChatListSchema(Schema):
    chats = fields.List(fields.Nested(ChatSchema()))


class PlayerSchema(Schema):
    tg_user_id = fields.Int(required=True)
    name = fields.Str(required=True)
    balance = fields.Int(required=True)
    # chats = fields.List(fields.Nested(ChatSchema()))


class PlayerListSchema(Schema):
    players = fields.List(fields.Nested(PlayerSchema()))


class GameSchema(Schema):
    id = fields.Int(required=True)
    tg_chat_id = fields.Int(required=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=False)
    players = fields.List(fields.Nested(PlayerSchema()))


class GameListSchema(Schema):
    games = fields.List(fields.Nested(GameSchema()))
