import logging
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pyrogram import Client as PyrogramClient, enums
from pyrogram.enums import ChatAction
from starlette import status


class ResponseStatus(str, Enum):
    OK: str = 'OK'
    NOT_READY: str = 'NOT_READY'
    BAD_REQUEST: str = 'BAD_REQUEST'
    INTERNAL_SERVER_ERROR: str = 'INTERNAL_SERVER_ERROR'
    TOO_MANY_REQUESTS: str = 'TOO_MANY_REQUESTS'
    NOT_FOUND: str = 'NOT_FOUND'


class SendMessageRequest(BaseModel):
    text: str = Field()
    reply_to: Optional[str] = Field()
    chat_id: str = Field(min_length=1)


class BasicResponse(BaseModel):
    error_message: Optional[str] = Field(None)
    status: ResponseStatus = Field(None)

    class Config:
        use_enum_values = True


class SendMessageResponse(BasicResponse):
    message_id: Optional[str] = Field(None)

    class Config:
        use_enum_values = True


class ChatAdminsResponse(BasicResponse):
    admin_ids: Optional[list] = Field(None)

    class Config:
        use_enum_values = True


class Controller:
    def __init__(self, pyrogram_client: PyrogramClient):
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.pyrogram_client = pyrogram_client
        self.router = APIRouter()

        self.router.add_api_route('/text-messages', self.send_message, methods=['POST'])
        self.router.add_api_route('/chats/{chat_id}/actions/typing', self.send_typing_action, methods=['POST'])
        self.router.add_api_route('/chats/{chat_id}/admins', self.get_admins, methods=['GET'])

    async def send_typing_action(self, chat_id: str = Path()) -> JSONResponse:
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

    async def get_admins(self, chat_id: str = Path()) -> JSONResponse:
        try:
            admins = self.pyrogram_client.get_chat_members(chat_id=chat_id,
                                                           filter=enums.ChatMembersFilter.ADMINISTRATORS)
            admin_ids = set()
            async for admin in admins:
                admin_ids.add(str(admin.user.id))
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ChatAdminsResponse(
                    status=ResponseStatus.OK,
                    admin_ids=list(admin_ids),
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

    async def send_message(self, request: SendMessageRequest) -> JSONResponse:
        try:
            sent_message = await self.pyrogram_client.send_message(
                chat_id=int(request.chat_id),
                text=request.text,
                reply_to_message_id=int(request.reply_to) if request.reply_to is not None else None
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=SendMessageResponse(
                    status=ResponseStatus.OK,
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
                    status=ResponseStatus.OK,
                    error_message=f'{str(e)}'
                ).dict(exclude_none=True)
            )
