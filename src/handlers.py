import dataclasses
import logging

import aiohttp
import pyrogram
from aiohttp import ClientError
from pyrogram import Client
from pyrogram.types import Message as PyrogramMessage, User, Chat

from new_message_request import NewMessageUser, NewMessageChat, NewMessageRequest
from pyrogram_utils import get_fullname, get_message_type, get_chat_type, \
    get_action_info, get_media_type


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
