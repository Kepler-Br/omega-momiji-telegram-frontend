import logging
from asyncio import AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor

import pyrogram
from confluent_kafka import Producer
from miniopy_async import Minio
from pyrogram import Client
from pyrogram.types import Message as PyrogramMessage


def register_kafka_handler(
        client: Client,
        group: int,
        minio: Minio,
        kafka_producer: Producer,
        event_loop: AbstractEventLoop):
    log = logging.getLogger(f'{__name__}.register_kafka_handler')

    def produce(topic: str, value: str) -> None:
        kafka_producer.produce(topic=topic, value=value)

    async def __prometheus_handler(_: Client, pyrogram_message: PyrogramMessage):
        await event_loop.run_in_executor(None, produce, "", "")

    client.add_handler(pyrogram.handlers.MessageHandler(__prometheus_handler, filters=None), group=group)
