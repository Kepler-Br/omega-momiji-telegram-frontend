import dataclasses
import logging

import aiohttp
import pyrogram
from aiohttp import ClientError
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import Message as PyrogramMessage, User, Chat

from new_message_request import NewMessageUser, NewMessageChat, NewMessageRequest
from pyrogram_utils import get_fullname, get_message_type, get_chat_type, \
    get_action_info, get_media_type
from src.prometheus_metrics import prometheus_pyrogram_messages, prometheus_pyrogram_messages_media, \
    prometheus_pyrogram_messages_service, prometheus_pyrogram_messages_text, prometheus_pyrogram_messages_caption, \
    prometheus_pyrogram_messages_document, prometheus_pyrogram_messages_forwards, \
    prometheus_pyrogram_messages_group_chat_created, prometheus_pyrogram_messages_left_chat_members, \
    prometheus_pyrogram_messages_location, prometheus_pyrogram_messages_new_chat_members, \
    prometheus_pyrogram_messages_new_chat_photo, prometheus_pyrogram_messages_new_chat_title, \
    prometheus_pyrogram_messages_photo, prometheus_pyrogram_messages_pinned_message, prometheus_pyrogram_messages_poll, \
    prometheus_pyrogram_messages_reactions, prometheus_pyrogram_messages_sticker, \
    prometheus_pyrogram_messages_supergroup_chat_created, prometheus_pyrogram_messages_video_chat_ended, \
    prometheus_pyrogram_messages_video_chat_started, prometheus_pyrogram_messages_video, \
    prometheus_pyrogram_messages_video_note, prometheus_pyrogram_messages_voice, \
    prometheus_pyrogram_known_private_chats, prometheus_pyrogram_known_group_chats, \
    prometheus_pyrogram_known_supergroup_chats, prometheus_pyrogram_known_channel_chats, \
    prometheus_pyrogram_known_bot_chats, prometheus_pyrogram_known_unknown_chats


def pyrogram_user_to_dto_user(value: User) -> NewMessageUser:
    return NewMessageUser(
        id=str(value.id),
        username=value.username,
        fullname=get_fullname(value),
    )


def pyrogram_chat_to_dto_chat(value: Chat) -> NewMessageChat:
    return NewMessageChat(
        id=str(value.id),
        title=value.title,
        type=get_chat_type(value),
    )


def register_gateway_handler(
        client: Client,
        message_gateway_addresses: list[str],
        frontend_name: str,
        group: int = -458155
):
    log = logging.getLogger(f'{__name__}.gateway_logging_handler')

    async def __gateway_logging_handler(_: Client, pyrogram_message: PyrogramMessage):
        author = pyrogram_user_to_dto_user(pyrogram_message.from_user)
        chat = pyrogram_chat_to_dto_chat(pyrogram_message.chat)
        message_type = get_message_type(pyrogram_message)
        action_info = get_action_info(pyrogram_message)
        media_type = get_media_type(pyrogram_message)

        message = NewMessageRequest(
            id=str(pyrogram_message.id),
            author=author,
            chat=chat,
            frontend=frontend_name,
            text=pyrogram_message.text,
            type=message_type,
            reply_to=str(pyrogram_message.reply_to_message_id),
            action_info=action_info,
            media_type=media_type,
        )

        for gateway_address in message_gateway_addresses:
            async with aiohttp.ClientSession() as session:
                try:
                    response = await session.put(
                        f'{gateway_address}/inbound/messages',
                        json=dataclasses.asdict(message)
                    )

                    status = response.status
                    if status != 200:
                        log.error(
                            f'Unexpected answer from gateway "{gateway_address}"\n'
                            f'Status: {status}\n'
                            f'Body:{await response.text()}')
                except RuntimeError as e:
                    # TODO: RuntimeError not caught
                    log.error(f'Exception raised while sending new message to gateway "{gateway_address}":')
                    log.error(e, exc_info=True)
                except ClientError as e:
                    log.error(f'Exception raised while sending new message to gateway "{gateway_address}":')
                    log.error(e, exc_info=True)
                finally:
                    await session.close()

    client.add_handler(pyrogram.handlers.MessageHandler(__gateway_logging_handler, filters=None), group=group)


def register_prometheus_handler(client: Client, group: int = -458155):
    known_private_chats: set[int] = set()
    known_group_chats: set[int] = set()
    known_supergroup_chats: set[int] = set()
    known_bot_chats: set[int] = set()
    known_channel_chats: set[int] = set()
    known_unknown_chats: set[int] = set()
    async def __prometheus_handler(_: Client, pyrogram_message: PyrogramMessage):
        prometheus_pyrogram_messages.inc()
        if pyrogram_message.chat.type == ChatType.PRIVATE:
            known_private_chats.add(pyrogram_message.chat.id)
            prometheus_pyrogram_known_private_chats.set(len(known_private_chats))
        elif pyrogram_message.chat.type == ChatType.GROUP:
            known_group_chats.add(pyrogram_message.chat.id)
            prometheus_pyrogram_known_group_chats.set(len(known_group_chats))
        elif pyrogram_message.chat.type == ChatType.SUPERGROUP:
            known_supergroup_chats.add(pyrogram_message.chat.id)
            prometheus_pyrogram_known_supergroup_chats.set(len(known_supergroup_chats))
        elif pyrogram_message.chat.type == ChatType.CHANNEL:
            known_channel_chats.add(pyrogram_message.chat.id)
            prometheus_pyrogram_known_channel_chats.set(len(known_channel_chats))
        elif pyrogram_message.chat.type == ChatType.BOT:
            known_bot_chats.add(pyrogram_message.chat.id)
            prometheus_pyrogram_known_bot_chats.set(len(known_bot_chats))
        else:
            known_unknown_chats.add(pyrogram_message.chat.id)
            prometheus_pyrogram_known_unknown_chats.set(len(known_unknown_chats))

        if pyrogram_message.caption is not None:
            prometheus_pyrogram_messages_caption.inc()
        if pyrogram_message.document is not None:
            prometheus_pyrogram_messages_document.inc()
        if pyrogram_message.forwards is not None:
            prometheus_pyrogram_messages_forwards.inc()
        if pyrogram_message.group_chat_created is not None:
            prometheus_pyrogram_messages_group_chat_created.inc()
        if pyrogram_message.left_chat_member is not None:
            prometheus_pyrogram_messages_left_chat_members.inc()
        if pyrogram_message.location is not None:
            prometheus_pyrogram_messages_location.inc()
        if pyrogram_message.media is not None:
            prometheus_pyrogram_messages_media.inc()
        if pyrogram_message.new_chat_members is not None:
            prometheus_pyrogram_messages_new_chat_members.inc()
        if pyrogram_message.new_chat_photo is not None:
            prometheus_pyrogram_messages_new_chat_photo.inc()
        if pyrogram_message.new_chat_title is not None:
            prometheus_pyrogram_messages_new_chat_title.inc()
        if pyrogram_message.photo is not None:
            prometheus_pyrogram_messages_photo.inc()
        if pyrogram_message.pinned_message is not None:
            prometheus_pyrogram_messages_pinned_message.inc()
        if pyrogram_message.poll is not None:
            prometheus_pyrogram_messages_poll.inc()
        if pyrogram_message.reactions is not None:
            prometheus_pyrogram_messages_reactions.inc()
        if pyrogram_message.service is not None:
            prometheus_pyrogram_messages_service.inc()
        if pyrogram_message.sticker is not None:
            prometheus_pyrogram_messages_sticker.inc()
        if pyrogram_message.supergroup_chat_created is not None:
            prometheus_pyrogram_messages_supergroup_chat_created.inc()
        if pyrogram_message.text is not None:
            prometheus_pyrogram_messages_text.inc()
        if pyrogram_message.video_chat_ended is not None:
            prometheus_pyrogram_messages_video_chat_ended.inc()
        if pyrogram_message.video_chat_started is not None:
            prometheus_pyrogram_messages_video_chat_started.inc()
        if pyrogram_message.video is not None:
            prometheus_pyrogram_messages_video.inc()
        if pyrogram_message.video_note is not None:
            prometheus_pyrogram_messages_video_note.inc()
        if pyrogram_message.voice is not None:
            prometheus_pyrogram_messages_voice.inc()

    client.add_handler(pyrogram.handlers.MessageHandler(__prometheus_handler, filters=None), group=group)


def register_logging_handler(client: Client, group: int = -458156):
    log = logging.getLogger(f'{__name__}.logging_handler')

    async def __logging_handler(_: Client, pyrogram_message: PyrogramMessage):
        result = f'Incoming message: {pyrogram_message.id}\n'
        # Chat info
        if pyrogram_message.chat.title is not None:
            result += f'From chat: {pyrogram_message.chat.title} ({pyrogram_message.chat.id})\n'
        else:
            fullname = pyrogram_message.chat.first_name + pyrogram_message.chat.last_name if pyrogram_message.chat.last_name else ''
            result += f'From chat: @{pyrogram_message.chat.username} "{fullname}" ({pyrogram_message.chat.id})\n'

        # User info
        result += f'From user: @{pyrogram_message.from_user.username} "{pyrogram_message.from_user.first_name} {pyrogram_message.from_user.last_name}" ({pyrogram_message.from_user.id})\n'

        # Media
        if pyrogram_message.media is not None:
            result += f'Media: {pyrogram_message.media.name}\n'

        # Service
        if pyrogram_message.service is not None:
            result += f'Service: {pyrogram_message.service.name}\n'

        # Text
        if pyrogram_message.text is not None:
            result += f'Text: {pyrogram_message.text}\n'

        # Caption
        if pyrogram_message.caption is not None:
            result += f'Caption: {pyrogram_message.caption}\n'

        log.info(result.strip())

    client.add_handler(pyrogram.handlers.MessageHandler(__logging_handler, filters=None), group=group)
