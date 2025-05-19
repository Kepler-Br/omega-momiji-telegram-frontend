import logging
import pathlib
from asyncio import AbstractEventLoop
from io import BytesIO
from typing import Optional, Set

import pyrogram
from confluent_kafka import Producer
from miniopy_async import Minio
from pydantic import ValidationError
from pyrogram import Client
from pyrogram.types import Message as PyrogramMessage

from src.new_message import User, Chat, ChatType, NewMessage, MediaType


def pyrogram_mediatype_to_mediatype(value: Optional[pyrogram.enums.MessageMediaType]) -> Optional[MediaType]:
    if value is None:
        return None
    match value:
        case pyrogram.enums.MessageMediaType.STICKER:
            return MediaType.STICKER
        case pyrogram.enums.MessageMediaType.AUDIO:
            return MediaType.AUDIO
        case pyrogram.enums.MessageMediaType.VOICE:
            return MediaType.VOICE
        case pyrogram.enums.MessageMediaType.PHOTO:
            return MediaType.PHOTO
        case pyrogram.enums.MessageMediaType.VIDEO:
            return MediaType.VIDEO
        case pyrogram.enums.MessageMediaType.ANIMATION:
            return MediaType.ANIMATION
        case pyrogram.enums.MessageMediaType.VIDEO_NOTE:
            return MediaType.VIDEO_NOTE
        case _:
            return MediaType.OTHER


def pyrogram_user_to_user(value: Optional[pyrogram.types.User]) -> Optional[User]:
    if value is None:
        return None

    return User(
        id=str(value.id),
        first_name=value.first_name,
        last_name=value.last_name,
        username=value.username,
        is_bot=value.is_bot,
    )


def pyrogram_chat_to_chat(value: Optional[pyrogram.types.Chat]) -> Optional[Chat]:
    if value is None:
        return None

    chat_type: ChatType
    match value.type:
        case pyrogram.enums.ChatType.PRIVATE:
            chat_type = ChatType.PRIVATE
        case pyrogram.enums.ChatType.BOT:
            chat_type = ChatType.PRIVATE
        case pyrogram.enums.ChatType.GROUP:
            chat_type = ChatType.GROUP
        case pyrogram.enums.ChatType.SUPERGROUP:
            chat_type = ChatType.GROUP
        case pyrogram.enums.ChatType.CHANNEL:
            chat_type = ChatType.GROUP
        case _:
            return None

    chat_title: str
    if chat_type == ChatType.PRIVATE:
        if value.first_name is None and value.last_name is not None:
            chat_title = value.last_name
        elif value.first_name is not None and value.last_name is None:
            chat_title = value.first_name
        elif value.first_name is not None and value.last_name is not None:
            chat_title = f'{value.first_name} {value.last_name}'
        elif value.username is not None:
            chat_title = value.username
        elif value.title is not None:
            chat_title = value.title
        else:
            chat_title = str(value.id)
    else:
        chat_title = value.title

    return Chat(
        id=str(value.id),
        title=chat_title,
        type=chat_type
    )


def register_kafka_handler(
        client: Client,
        group: int,
        minio: Minio,
        kafka_producer: Producer,
        event_loop: AbstractEventLoop,
        frontend: str,
        topic: str,
        max_file_size: int,
        whitelist: Set[int],
):
    log = logging.getLogger(f'{__name__}.register_kafka_handler')

    def produce(topic: str, key: str, value: str) -> None:
        kafka_producer.produce(topic=topic, key=key, value=value)

    async def __kafka_handler(_: Client, message: PyrogramMessage):
        if message.chat.id not in whitelist:
            return
        try:
            user = pyrogram_user_to_user(message.from_user)
            forwarded_from = pyrogram_user_to_user(message.forward_from)
            chat = pyrogram_chat_to_chat(message.chat)
            kafka_message = NewMessage(
                user=user,
                chat=chat,
                forward_from=forwarded_from,
                frontend=frontend,
                text=message.text,
                reply_to_message_id=message.reply_to_message_id,
                media_type=pyrogram_mediatype_to_mediatype(message.media),
                s3_bucket=None,
                s3_object=None,
            )
        except ValidationError as e:
            log.error('Contract violation! Expected fields were not filled: %s', e)
            return
        if message.photo is not None:
            if kafka_message.media_type != MediaType.PHOTO:
                log.warning('message.photo is not None, yet MediaType is not PHOTO')
            if message.photo.file_size < max_file_size:
                downloaded: BytesIO = await message.download(in_memory=True, block=True)
                # TODO: Sounds like shit. Probably we should not seek this
                downloaded.seek(0)
                # TODO: Test if pathlib raises error if no suffix found
                object_name = str(message.photo.file_id) + pathlib.Path(downloaded.name).suffix
                await minio.put_object(
                    bucket_name='photo',
                    object_name=object_name,
                    data=downloaded,
                    length=message.photo.file_size,
                )
                downloaded.close()
                kafka_message.s3_bucket = 'photo'
                kafka_message.s3_object = object_name
            pass
        try:
            await event_loop.run_in_executor(
                None,
                produce,
                topic,
                kafka_message.chat.id,
                kafka_message.model_dump_json()
            )
        except Exception as e:
            log.error(e)

    client.add_handler(pyrogram.handlers.MessageHandler(__kafka_handler, filters=None), group=group)
