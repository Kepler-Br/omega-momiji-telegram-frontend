import dataclasses
import json
import logging
import os
from io import BytesIO
from typing import List

import uvicorn
import yaml
from confluent_kafka import Producer
from miniopy_async import Minio

from pydantic import BaseModel, Field

from new_message_request import NewMessageRequest, NewMessageUser, NewMessageChat, ChatType, MessageType
from src.tools import convert_string_size_to_bytes, get_dict_key_by_path


class S3Config(BaseModel):
    url: str = Field(min_length=1)

    class Config:
        validate_by_name = True


class KafkaConfig(BaseModel):
    bootstrap_servers: str = Field(min_length=1)
    messages_topic: str = Field(min_length=1)


class FrontendConfig(BaseModel):
    name: str = Field(min_length=1)
    max_file_size: int = Field()
    upload_files: bool = Field(default=True)
    whitelist: List[int] = Field()


def main():
    with open('config.yaml') as fp:
        conf = yaml.load(fp, Loader=yaml.FullLoader)
    s3_config = S3Config(url=get_dict_key_by_path(conf, 's3.url'))
    kafka_config = KafkaConfig(
        bootstrap_servers=get_dict_key_by_path(conf, 'kafka.bootstrap.servers'),
        messages_topic=get_dict_key_by_path(conf, 'kafka.messages.topic'),
    )
    frontend_config = FrontendConfig(
        name=get_dict_key_by_path(conf, 'frontend.name'),
        max_file_size=convert_string_size_to_bytes(get_dict_key_by_path(conf, 'frontend.max-file-size')),
        upload_files=get_dict_key_by_path(conf, 'frontend.upload-files', fail=False),
        whitelist=get_dict_key_by_path(conf, 'frontend.chat.whitelist'),
    )

    print(s3_config)
    print(kafka_config)
    print(frontend_config)
    logging.basicConfig()
    log = logging.getLogger(f'{__name__}.main')
    # log.setLevel(logging.DEBUG)

    log.fatal('fatal')
    log.critical('critical')
    log.error('error')
    log.info('info')
    log.debug('debug')

    return
    config = {
        'bootstrap.servers': 'localhost:9092',
    }

    producer = Producer(config)

    def send_message(topic, message):
        producer.produce(topic, value=message)
        producer.flush()

    new_message = NewMessageRequest(
        id='4',
        author=NewMessageUser(
            id='5267243',
            username='Me',
            fullname='Firstname Secondname',
        ),
        chat=NewMessageChat(
            id='-65347681423',
            title='Omega Momiji',
            type=ChatType.GROUP,
        ),
        frontend='Telegram 1',
        type=MessageType.MESSAGE,
        reply_to='3',
        text='Hello World!',
    )

    send_message(
        'frontends.messages.v1',
        json.dumps(
            dataclasses.asdict(new_message),
            indent=2,
            ensure_ascii=False
        )
    )
    access_key = os.environ.get('MINIO_ACCESS_KEY')
    secret_key = os.environ.get('MINIO_SECRET_KEY')
    client = Minio("localhost:8000",
                   secure=False,
                   access_key=access_key,
                   secret_key=secret_key,
                   )
    print(
        client.bucket_exists("audio1")
    )
    with open("/home/kepler-br/Music/Ib/title.mp3", "rb") as fp:
        read = fp.read()

        client.put_object("audio", "audio_test.mp3", BytesIO(read), len(read))
    pass


if __name__ == '__main__':
    # main()
    # sys.exit(0)
    port: int = int(os.environ.get('SERVER_PORT', '8080'))
    host: str = os.environ.get('SERVER_HOST', '0.0.0.0')

    uvicorn.run("main:fastapi_app", host=host, port=port, reload=False, workers=1, log_config='logging.yaml')
