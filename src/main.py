# TODO: Fix logging. Can't set DEBUG level
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

from src.config import get_configurations
from src.handlers.kafka_handler import register_kafka_handler
from src.handlers.logging_handler import register_logging_handler
from src.handlers.prometheus_handler import register_prometheus_handler


class ProgramArguments(BaseModel):
    log_level: str = Field('INFO', min_length=1)
    bot_token: str = Field(min_length=1)
    api_hash: str = Field(min_length=1)
    api_id: str = Field(min_length=1)
    s3_access_key: str = Field(min_length=1)
    s3_secret_key: str = Field(min_length=1)


def parse_arguments() -> ProgramArguments:
    try:
        return ProgramArguments(
            log_level=os.environ.get('SERVER_LOG_LEVEL', 'INFO'),
            bot_token=os.environ.get('BOT_TOKEN'),
            api_hash=os.environ.get('API_HASH'),
            api_id=os.environ.get('API_ID'),
            s3_access_key=os.environ.get('S3_ACCESS_KEY'),
            s3_secret_key=os.environ.get('S3_SECRET_KEY'),
        )
    except pydantic.error_wrappers.ValidationError as e:
        print(e)
        sys.exit(-1)


arguments = parse_arguments()

with open('config.yaml') as fp:
    conf = yaml.load(fp, Loader=yaml.FullLoader)

s3_config, kafka_config, frontend_config = get_configurations(conf)
# Configure logging
# with open('logging.yaml') as fp:
#     conf = yaml.load(fp, Loader=yaml.FullLoader)
#
# conf['root']['level'] = arguments.log_level

logging.basicConfig()
main_logger = logging.getLogger('__main__')
logging.debug('lol')
main_logger.debug('lol')
# logging.config.dictConfig(conf)

logging.debug('lol')
main_logger.debug('lol')

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


@fastapi_app.on_event("startup")
async def startup_event():
    log.info('Application startup')
    await pyrogram_app.start()
    loop = asyncio.get_event_loop()

    config = {
        'bootstrap.servers': kafka_config.bootstrap_servers,
    }
    register_logging_handler(client=pyrogram_app, group=-458155)
    register_prometheus_handler(client=pyrogram_app, group=-458156)

    minio = Minio(s3_config.url,
                  secure=False,
                  access_key=arguments.s3_access_key,
                  secret_key=arguments.s3_secret_key,
                  )
    register_kafka_handler(
        client=pyrogram_app,
        group=-458157,
        minio=minio,
        kafka_producer=Producer(config),
        event_loop=loop,
        frontend=frontend_config.name,
        topic=kafka_config.messages_topic,
        max_file_size=frontend_config.max_file_size,
        whitelist=set(frontend_config.whitelist),
    )


@fastapi_app.on_event("shutdown")
async def shutdown_event():
    log.info('Application shutdown')
    await pyrogram_app.stop()


controller = Controller(pyrogram_client=pyrogram_app)

fastapi_app.include_router(controller.router)
