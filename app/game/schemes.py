from marshmallow import Schema, fields


class ChatSchema(Schema):
    chat_id = fields.Int(required=True)


class ChatListSchema(Schema):
    chats = fields.List(fields.Nested(ChatSchema()))


class PlayerSchema(Schema):
    user_id = fields.Int(required=True)
    name = fields.Str(required=True)


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


class ScoreSchema(Schema):
    captain_name = fields.Str()
    captain_id = fields.Int()
    game_id = fields.Int()
    # callback_id = fields.Int()
    # start_round = fields.Int()
    # finish_round = fields.Int()
    # choice_questions = fields.Boolean()
    # timer_tour = fields.Boolean()
    # get_answer = fields.Boolean()
    score_bot = fields.Int()
    score_team = fields.Int()
    winner = fields.Str()


class ScoreListSchema(Schema):
    scores = fields.List(fields.Nested(ScoreSchema()))


class TourSchema(Schema):
    id = fields.Int()
    question_id = fields.Int()
    game_id = fields.Int()


class TourListSchema(Schema):
    tours = fields.List(fields.Nested(TourSchema()))
