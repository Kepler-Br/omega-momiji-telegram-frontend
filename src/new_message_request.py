from dataclasses import dataclass
from typing import Optional


@dataclass
class NewMessageUser:
    id: str
    username: str
    fullname: str


class ChatType:
    GROUP = 'GROUP'
    PRIVATE = 'PRIVATE'


class ActionType:
    NEW_MEMBER = 'NEW_MEMBER'
    MEMBER_LEFT = 'MEMBER_LEFT'
    OTHER = 'OTHER'


class MessageType:
    MESSAGE = 'MESSAGE'
    ACTION = 'ACTION'
    OTHER = 'OTHER'


@dataclass
class NewMessageChat:
    id: str
    title: str
    type: str


@dataclass
class NewMessageActionInfo:
    action_type: str
    related_user: NewMessageUser


@dataclass
class NewMessageRequest:
    id: str
    author: NewMessageUser
    chat: NewMessageChat
    frontend: str
    type: str
    text: Optional[str] = None
    action_info: Optional[NewMessageActionInfo] = None
