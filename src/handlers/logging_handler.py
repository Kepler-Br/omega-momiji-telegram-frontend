import logging

import pyrogram
from pyrogram import Client
from pyrogram.types import Message as PyrogramMessage


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
