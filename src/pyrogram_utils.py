from typing import Optional

from pyrogram import types
from pyrogram.enums import MessageServiceType, MessageMediaType
from pyrogram.types import Message as PyrogramMessage, Chat

from new_message_request import NewMessageUser, ChatType, MessageType, ActionType, NewMessageActionInfo, MediaType


def get_fullname(user: types.User) -> Optional[str]:
    if user.first_name is None and user.last_name is None:
        return None

    if user.first_name is not None and user.last_name is None:
        return user.first_name

    if user.first_name is None and user.last_name is not None:
        return user.last_name

    return f'{user.first_name} {user.last_name}'


def get_chat_type(value: Chat) -> str:
    return ChatType.GROUP if value.id < 0 else ChatType.PRIVATE


def get_action_related_user(value: PyrogramMessage) -> NewMessageUser:
    if value.left_chat_member is not None:
        return NewMessageUser(
            id=str(value.left_chat_member.id),
            username=value.left_chat_member.username,
            fullname=get_fullname(value.left_chat_member),
        )
    elif value.new_chat_members is not None:
        new_chat_member = value.new_chat_members[0]

        return NewMessageUser(
            id=str(new_chat_member.id),
            username=new_chat_member.username,
            fullname=get_fullname(new_chat_member),
        )

    raise RuntimeError("Unknown action type for related user")


def get_action_type(value: PyrogramMessage) -> str:
    if value.service == MessageServiceType.NEW_CHAT_MEMBERS:
        return ActionType.NEW_MEMBER
    elif value.service == MessageServiceType.LEFT_CHAT_MEMBERS:
        return ActionType.MEMBER_LEFT
    else:
        return ActionType.OTHER


def get_message_type(value: PyrogramMessage) -> str:
    if value.service == MessageServiceType.LEFT_CHAT_MEMBERS or value.service == MessageServiceType.NEW_CHAT_MEMBERS:
        return MessageType.ACTION
    if value.service is not None:
        return MessageType.OTHER
    return MessageType.MESSAGE


def get_action_info(value: PyrogramMessage) -> Optional[NewMessageActionInfo]:
    """
    Will return null if message is not an action
    :param value: pyrogram message instance
    """

    message_type = get_message_type(value)

    if message_type == MessageType.ACTION:
        return NewMessageActionInfo(
            action_type=get_action_type(value),
            related_user=get_action_related_user(value),
        )
    return None


def get_media_type(value: PyrogramMessage) -> Optional[MediaType]:
    """
    Will return null if message has no media in it
    :param value: pyrogram message instance
    """

    if value.media == MessageMediaType.ANIMATION:
        return MediaType.GIF
    if value.media == MessageMediaType.VIDEO:
        return MediaType.VIDEO
    if value.media == MessageMediaType.VOICE:
        return MediaType.VOICE
    if value.media == MessageMediaType.VIDEO_NOTE:
        return MediaType.VIDEO_NOTE
    if value.media == MessageMediaType.AUDIO:
        return MediaType.AUDIO
    if value.media == MessageMediaType.PHOTO:
        return MediaType.PHOTO
    if value.media == MessageMediaType.STICKER:
        return MediaType.STICKER

    return None
