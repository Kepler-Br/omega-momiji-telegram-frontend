from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ChatType(str, Enum):
    PRIVATE = 'PRIVATE'
    GROUP = 'GROUP'


class MediaType(str, Enum):
    STICKER = 'STICKER'
    AUDIO = 'AUDIO'
    VOICE = 'VOICE'
    PHOTO = 'PHOTO'
    VIDEO = 'VIDEO'
    ANIMATION = 'ANIMATION'
    VIDEO_NOTE = 'VIDEO_NOTE'
    OTHER = 'OTHER'


class Chat(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    type: ChatType = Field()


class User(BaseModel):
    id: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    last_name: Optional[str] = Field(None)
    username: str = Field(min_length=1)
    is_bot: bool = Field()


class NewMessage(BaseModel):
    user: User = Field()
    chat: Chat = Field()
    forward_from: Optional[User] = Field(None)
    frontend: str = Field()
    text: Optional[str] = Field()
    reply_to_message_id: Optional[str] = Field(None)
    media_type: Optional[MediaType] = Field(None)
    s3_bucket: Optional[str] = Field(None)
    s3_object: Optional[str] = Field(None)
