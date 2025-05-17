import dataclasses
import logging

import aiohttp
import pyrogram
from aiohttp import ClientError
from pyrogram import Client
from pyrogram.types import Message as PyrogramMessage, User, Chat

from src.new_message_request import NewMessageUser, NewMessageChat, NewMessageRequest
from src.pyrogram_utils import get_fullname, get_chat_type, get_action_info, get_message_type, get_media_type


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
