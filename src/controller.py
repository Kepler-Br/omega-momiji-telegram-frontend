import logging
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from pyrogram import Client as PyrogramClient
from pyrogram.enums import ChatAction
from starlette import status


class ResponseStatus:
    OK = 'OK'
    TOO_EARLY = 'TOO_EARLY'
    BAD_REQUEST = 'BAD_REQUEST'
    INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'
    NOT_FOUND = 'NOT_FOUND'


class SendMessageRequest(BaseModel):
    text: str = Field()
    reply_to: Optional[str] = Field()
    chat_id: str = Field(min_length=1)


class SendMessageResponse(BaseModel):
    error_message: Optional[str] = Field(None)
    message_id: Optional[str] = Field(None)


class BasicResponse(BaseModel):
    error_message: Optional[str] = Field(None)
    status: str = Field()


class Controller:
    def __init__(self, pyrogram_client: PyrogramClient):
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.pyrogram_client = pyrogram_client
        self.router = APIRouter()

        self.router.add_api_route('/text-messages', self.send_message, methods=['POST'])
        self.router.add_api_route('/actions/typing', self.send_typing_action, methods=['POST'])

    async def send_typing_action(self, chat_id: str) -> Response:
        try:
            await self.pyrogram_client.send_chat_action(chat_id, ChatAction.TYPING)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=BasicResponse(
                    status=ResponseStatus.OK
                ).dict(exclude_none=True)
            )
        except RuntimeError as e:
            self.log.error(e, exc_info=True)

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=BasicResponse(
                    status=ResponseStatus.INTERNAL_SERVER_ERROR,
                    error_message=f'{e.__class__.__name__}: {e}'
                ).dict(exclude_none=True)
            )

    async def send_message(self, request: SendMessageRequest) -> Response:
        try:
            sent_message = await self.pyrogram_client.send_message(
                chat_id=int(request.chat_id),
                text=request.text,
                reply_to_message_id=int(request.reply_to) if request.reply_to is not None else None
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=SendMessageResponse(
                    message_id=str(sent_message.id)
                ).dict(exclude_none=True)
            )
        except RuntimeError as e:
            self.log.error('Error while trying to send message with parameters:\n'
                           f'{request.json()}')
            self.log.error(e, exc_info=True)

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=SendMessageResponse(
                    error_message=f'{str(e)}'
                ).dict(exclude_none=True)
            )
