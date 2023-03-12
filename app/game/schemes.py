from marshmallow import Schema, fields


class ChatSchema(Schema):
    chat_id = fields.Int(required=True)


class ChatListSchema(Schema):
    chats = fields.List(fields.Nested(ChatSchema()))


class PlayerSchema(Schema):
    user_id = fields.Int(required=True)
    name = fields.Str(required=True)
    balance = fields.Int(required=True)
    # chats = fields.List(fields.Nested(ChatSchema()))


class PlayerListSchema(Schema):
    players = fields.List(fields.Nested(PlayerSchema()))


class GameSchema(Schema):
    id = fields.Int(required=True)
    chat_id = fields.Int(required=True)
    start_time = fields.DateTime(required=True)
    finish_time = fields.DateTime(required=False)
    players = fields.List(fields.Nested(PlayerSchema()))


class GameListSchema(Schema):
    games = fields.List(fields.Nested(GameSchema()))
