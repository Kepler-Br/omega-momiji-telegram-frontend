import dataclasses
import logging.config
import os
import sys

import aiohttp
import pydantic
import yaml
from fastapi import FastAPI
from pydantic import BaseModel, Field
from pyrogram.types import Message

from controller import Controller
from logging_client import LoggingClient
from new_message_request import NewMessageAuthor, NewMessageChat, ChatType, NewMessageRequest
from pyrogram_utils import get_fullname


class ProgramArguments(BaseModel):
    log_level: str = Field('INFO', alias='SERVER_LOG_LEVEL', min_length=1)
    message_gateway_addresses: list[str] = Field(alias='SERVER_MESSAGE_GATEWAY_ADDRESSES', min_length=1)
    bot_token: str = Field(alias='BOT_TOKEN', min_length=1)
    api_hash: str = Field(alias='API_HASH', min_length=1)
    api_id: str = Field(alias='API_ID', min_length=1)
    frontend_name: str = Field(alias='SERVER_FRONTEND_NAME', min_length=1)

    class Config:
        allow_population_by_field_name = True


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


@pyrogram_app.on_message
async def new_frontend_message(client, pyrogram_message: Message):
    author = NewMessageAuthor(
        id=str(pyrogram_message.from_user.id),
        username=pyrogram_message.from_user.username,
        fullname=get_fullname(pyrogram_message.from_user),
    )
    chat = NewMessageChat(
        id=str(pyrogram_message.id),
        title=pyrogram_message.chat.title,
        type=ChatType.GROUP if pyrogram_message.chat.id < 0 else ChatType.PRIVATE,
    )
    message = NewMessageRequest(
        id=str(pyrogram_message.id),
        author=author,
        chat=chat,
        frontend=arguments.frontend_name,
        text=pyrogram_message.text,
    )

    for gateway_address in arguments.message_gateway_addresses:
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.post(
                    f'{gateway_address}/inbound/messages',
                    json=dataclasses.asdict(message)
                )

                status = response.status
                if status != 200:
                    log.error(
                        f'Unexpected answer from gateway "{gateway_address}"\n'
                        f'Status: {status}\n'
                        f'Body:{await response.text()}')
                await session.close()
            except RuntimeError as e:
                log.error(
                    f'Exception raised while sending new message to gateway "{gateway_address}":'
                )
                log.error(e, exc_info=True)


controller = Controller(pyrogram_client=pyrogram_app)

fastapi_app.include_router(controller.router)
