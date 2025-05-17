from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ChatType(Enum):
    PRIVATE = 'PRIVATE'
    GROUP = 'GROUP'

class MediaType(Enum):
    STICKER = 'STICKER'
    AUDIO = 'AUDIO'
    VOICE = 'VOICE'
    PHOTO = 'PHOTO'
    VIDEO = 'VIDEO'
    GIF = 'GIF'
    VIDEO_NOTE = 'VIDEO_NOTE'

@dataclass
class Chat:
    id: str
    title: str
    type: ChatType

@dataclass
class User:
    id: str
    first_name: str
    last_name: str
    username: str
    is_bot: bool

@dataclass
class NewMessage:
    user: User
    chat: Chat
    forward_from: Optional[User]
    frontend: str
    text: Optional[str]
    reply_to_message_id: Optional[str]
    media_type: Optional[MediaType]
    s3_bucket: Optional[str]
    s3_object: Optional[str]
