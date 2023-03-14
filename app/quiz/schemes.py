from marshmallow import Schema, fields


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    question = fields.Str(required=True)
    answer = fields.Str(required=True)


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)
