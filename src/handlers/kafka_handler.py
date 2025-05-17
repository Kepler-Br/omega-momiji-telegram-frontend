import logging
from asyncio import AbstractEventLoop
from typing import Optional

import pyrogram
from confluent_kafka import Producer
from miniopy_async import Minio
from pyrogram import Client
from pyrogram.types import Message as PyrogramMessage

from src.new_message import User, Chat


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

    return Chat(
    id=str(value.id),
    title=value.title,
    type=value.type, # TODO: convert to my enum
    )

def register_kafka_handler(
        client: Client,
        group: int,
        minio: Minio,
        kafka_producer: Producer,
        event_loop: AbstractEventLoop):
    log = logging.getLogger(f'{__name__}.register_kafka_handler')

    def produce(topic: str, value: str) -> None:
        kafka_producer.produce(topic=topic, value=value)

    async def __kafka_handler(_: Client, message: PyrogramMessage):
        user = pyrogram_user_to_user(message.from_user)
        forwarded_from = pyrogram_user_to_user(message.forward_from)
        message.chat
        await event_loop.run_in_executor(None, produce, "", "")

    client.add_handler(pyrogram.handlers.MessageHandler(__kafka_handler, filters=None), group=group)
