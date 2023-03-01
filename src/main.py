import logging.config
import os
import sys

import pydantic
import yaml
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.logging_client import LoggingClient


class ProgramArguments(BaseModel):
    log_level: str = Field('INFO', alias='SERVER_LOG_LEVEL', min_length=1)
    message_gateway_address: str = Field(alias='SERVER_MESSAGE_GATEWAY_ADDRESS', min_length=1)
    bot_token: str = Field(alias='BOT_TOKEN', min_length=1)
    api_hash: str = Field(alias='API_HASH', min_length=1)
    api_id: str = Field(alias='API_ID', min_length=1)

    class Config:
        allow_population_by_field_name = True


def parse_arguments() -> ProgramArguments:
    try:
        return ProgramArguments(
            log_level=os.environ.get('SERVER_LOG_LEVEL', 'INFO'),
            message_gateway_address=os.environ.get('SERVER_MESSAGE_GATEWAY_ADDRESS'),
            bot_token=os.environ.get('BOT_TOKEN'),
            api_hash=os.environ.get('API_HASH'),
            api_id=os.environ.get('API_ID'),
        )
    except pydantic.error_wrappers.ValidationError as e:
        print(e)
        sys.exit(-1)


arguments = parse_arguments()

# Configure logging
with open('logging.yaml') as fp:
    conf = yaml.load(fp, Loader=yaml.FullLoader)

conf['root']['level'] = arguments.log_level

logging.config.dictConfig(conf)

log = logging.getLogger(f'{__name__}.main')

pyrogram_app: LoggingClient = LoggingClient(
    name='omega_momiji',
    bot_token=arguments.bot_token,
    api_hash=arguments.api_hash,
    api_id=arguments.api_id
)

fastapi_app = FastAPI()


@fastapi_app.on_event("startup")
async def startup_event():
    await pyrogram_app.start()


@fastapi_app.on_event("shutdown")
async def shutdown_event():
    await pyrogram_app.stop()


@fastapi_app.get('/hell')
async def asd():
    await pyrogram_app.send_message(
        chat_id=0,
        text='Лол, работает'
    )
