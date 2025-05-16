import os
import sys
from io import BytesIO
from typing import BinaryIO

import uvicorn
from minio import Minio


def main():
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
