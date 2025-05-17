import dataclasses
import json
import os
import sys
from io import BytesIO

import uvicorn
from confluent_kafka import Producer
from miniopy_async import Minio

from new_message_request import NewMessageRequest, NewMessageUser, NewMessageChat, ChatType, MessageType


def main():
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
