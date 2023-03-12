import logging
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from pyrogram import Client as PyrogramClient
from starlette import status


class SendMessageRequest(BaseModel):
    text: Optional[str] = Field()
    reply_to: Optional[str] = Field()
    chat_id: str = Field(min_length=1)


class SendMessageResponse(BaseModel):
    error_message: Optional[str] = Field(None)
    message_id: Optional[str] = Field(None)


class Controller:
    def __init__(self, pyrogram_client: PyrogramClient):
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.pyrogram_client = pyrogram_client
        self.router = APIRouter()

        self.router.add_api_route('/text-messages', self.send_message, methods=['POST'])

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
                )
            )
        except RuntimeError as e:
            self.log.error('Error while trying to send message with parameters:\n'
                           f'{request.json()}')
            self.log.error(e, exc_info=True)

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=SendMessageResponse(
                    error_message=f'{str(e)}'
                )
            )
