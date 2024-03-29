from dataclasses import field
from typing import ClassVar, List, Optional, Type

from marshmallow import EXCLUDE, Schema
from marshmallow_dataclass import dataclass


@dataclass
class MessageFrom:
    id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str] = None

    class Meta:
        unknown = EXCLUDE

@dataclass
class CallbackFrom:
    id: int
    first_name: str
    username: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class Chat:
    id: int
    type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    title: Optional[str] = None

    class Meta:
        unknown = EXCLUDE

@dataclass
class ReplyMarkupData:
    text: str
    callback_data: str

    class Meta:
        unknown = EXCLUDE


# @dataclass
# class ReplyMarkup:
#     # # inline_keyboard: List[List[ReplyMarkupData]]
#     # data: int

#     class Meta:
#         unknown = EXCLUDE

# @dataclass
# class CallBackQuery:
#     data: int

#     class Meta:
#         unknown = EXCLUDE


@dataclass
class Message:
    message_id: int
    from_: MessageFrom = field(metadata={"data_key": "from"})
    chat: Chat
    text: Optional[str] = None
    # reply_markup: Optional[ReplyMarkupData] = None
    # callback_query: Optional[CallBackQuery] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class Callback:
    id: int
    from_: CallbackFrom = field(metadata={"data_key": "from"})
    message: Message
    data: int


    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    update_id: int
    message: Message = None
    callback_query: Callback = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: List[UpdateObj]

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE
