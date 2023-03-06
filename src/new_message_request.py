from dataclasses import dataclass


@dataclass
class NewMessageAuthor:
    id: str
    username: str
    fullname: str


class ChatType:
    GROUP = 'GROUP'
    PRIVATE = 'PRIVATE'


@dataclass
class NewMessageChat:
    id: str
    title: str
    type: str


@dataclass
class NewMessageRequest:
    author: NewMessageAuthor
    chat: NewMessageChat
    frontend: str
    id: str
    text: str
