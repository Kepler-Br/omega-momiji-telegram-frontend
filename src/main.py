# TODO: Fix logging. Can't set DEBUG level
# TODO: What needs to be done:
#       * minio client
#       * Whitelist
#       * Config file
#       * Media size limit
import asyncio
import logging.config
import os
import sys

from confluent_kafka import Producer
from miniopy_async import Minio

from controller import Controller
from fastapi import FastAPI
from prometheus_client import make_asgi_app
from pydantic import BaseModel, Field
from pyrogram import Client
import pydantic
import yaml

from src.handlers.kafka_handler import register_kafka_handler
from src.handlers.logging_handler import register_logging_handler
from src.handlers.prometheus_handler import register_prometheus_handler


class ProgramArguments(BaseModel):
    log_level: str = Field('INFO', alias='SERVER_LOG_LEVEL', min_length=1)
    message_gateway_addresses: list[str] = Field(alias='SERVER_MESSAGE_GATEWAY_ADDRESSES', min_length=1)
    bot_token: str = Field(alias='BOT_TOKEN', min_length=1)
    api_hash: str = Field(alias='API_HASH', min_length=1)
    api_id: str = Field(alias='API_ID', min_length=1)
    frontend_name: str = Field(alias='SERVER_FRONTEND_NAME', min_length=1)

    class Config:
        validate_by_name = True


def parse_arguments() -> ProgramArguments:
    try:
        gateway_address = os.environ.get('SERVER_MESSAGE_GATEWAY_ADDRESSES')
        return ProgramArguments(
            log_level=os.environ.get('SERVER_LOG_LEVEL', 'INFO'),
            message_gateway_addresses=gateway_address.split(';') if gateway_address is not None else None,
            bot_token=os.environ.get('BOT_TOKEN'),
            api_hash=os.environ.get('API_HASH'),
            api_id=os.environ.get('API_ID'),
            frontend_name=os.environ.get('SERVER_FRONTEND_NAME', 'telegram'),
        )
    except pydantic.error_wrappers.ValidationError as e:
        print(e)
        sys.exit(-1)


arguments = parse_arguments()

# Configure logging
with open('logging.yaml') as fp:
    conf = yaml.load(fp, Loader=yaml.FullLoader)

conf['root']['level'] = arguments.log_level

logging.basicConfig()
logging.config.dictConfig(conf)

log = logging.getLogger(f'{__name__}.main')

pyrogram_app: Client = Client(
    name='OmegaMomiji',
    bot_token=arguments.bot_token,
    api_hash=arguments.api_hash,
    api_id=arguments.api_id,
)

# register_gateway_handler(
#     client=pyrogram_app,
#     message_gateway_addresses=arguments.message_gateway_addresses,
#     frontend_name=arguments.frontend_name
# )


fastapi_app = FastAPI()

metrics_app = make_asgi_app()
fastapi_app.mount("/metrics", metrics_app)


def get_openapi():
    with open("static/frontend-contract.yaml", "r") as openapi:
        return yaml.load(openapi, Loader=yaml.FullLoader)


fastapi_app.openapi = get_openapi


@fastapi_app.get('/readiness')
async def readiness_probe():
    return {
        'readiness': True
    }


@fastapi_app.get('/liveness')
async def readiness_probe():
    return {
        'liveness': True
    }


@fastapi_app.on_event("startup")
async def startup_event():
    log.info('Application startup')
    await pyrogram_app.start()
    loop = asyncio.get_event_loop()

    config = {
        'bootstrap.servers': 'localhost:9092',
    }
    register_logging_handler(client=pyrogram_app, group=-458155)
    register_prometheus_handler(client=pyrogram_app, group=-458156)
    access_key = os.environ.get('MINIO_ACCESS_KEY')
    secret_key = os.environ.get('MINIO_SECRET_KEY')
    minio = Minio("localhost:8000",
                  secure=False,
                  access_key=access_key,
                  secret_key=secret_key,
                  )
    register_kafka_handler(
        client=pyrogram_app,
        group=-458157,
        minio=minio,
        kafka_producer=Producer(config),
        event_loop=loop,
        frontend='TODO',
        topic='frontends.messages.v1',
        max_file_size=10000,
    )


@fastapi_app.on_event("shutdown")
async def shutdown_event():
    log.info('Application shutdown')
    await pyrogram_app.stop()


controller = Controller(pyrogram_client=pyrogram_app)

fastapi_app.include_router(controller.router)
