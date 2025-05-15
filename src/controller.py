import logging
from typing import Optional, List

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from pyrogram import Client as PyrogramClient, enums
from starlette import status


class SendTextMessageRequest(BaseModel):
    text: str = Field()
    reply_to: Optional[str] = Field(None)


class SendMessageResponse(BaseModel):
    message_id: str = Field()


class SendMessageErrorResponse(BaseModel):
    error_message: str = Field()
    error_code: str = Field()


class GetAdminsResponse(BaseModel):
    admin_ids: List[int] = Field()


class Controller:
    def __init__(self,
                 pyrogram_client: PyrogramClient
                 ):
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.pyrogram_client = pyrogram_client
        self.router = APIRouter()

        self.router.add_api_route('/chats/{chat_id}/text-messages', self.send_text_message, methods=['POST'])
        self.router.add_api_route('/chats/{chat_id}/admins', self.get_chat_admins, methods=['GET'])
        self.router.add_api_route('/chats/{chat_id}/actions/typing', self.send_typing, methods=['POST'])
        self.router.add_api_route('/chats/{chat_id}/actions/typing', self.stop_typing, methods=['DELETE'])

    async def send_text_message(self, chat_id: str, request: SendTextMessageRequest) -> Response:
        self.log.info(f'Sending text message to chat_id {chat_id}')
        self.log.info(f'Body: {request.model_dump_json(indent=2)}')
        try:
            sent_message = await self.pyrogram_client.send_message(
                chat_id=int(chat_id),
                text=request.text,
                reply_to_message_id=int(request.reply_to) if request.reply_to is not None else None
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(
                    SendMessageResponse(
                        message_id=str(sent_message.id)
                    )
                )
            )
            # return JSONResponse(
            #     status_code=status.HTTP_200_OK,
            #     content=jsonable_encoder(
            #         SendMessageResponse(
            #             message_id=str(1337)
            #         )
            #     )
            # )
        except RuntimeError as e:
            self.log.error('Error while trying to send message with parameters:\n'
                           f'{request.model_dump_json()}')
            self.log.error(e, exc_info=True)

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(
                    SendMessageErrorResponse(
                        error_message=f'{str(e)}',
                        error_code='UNKNOWN_ERROR'
                    )
                )
            )
        except Exception as e:
            self.log.error('Unrecoverable exception while trying to send message')
            self.log.error(e, exc_info=True)
            raise e

    async def get_chat_admins(self, chat_id: str) -> Response:
        self.log.info(f'Getting chat admins for chat_id {chat_id}')
        self.log.info(f'::get_chat_admins unimplemented')
        try:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(GetAdminsResponse(admin_ids=[]))
            )
        except RuntimeError as e:
            self.log.error(f'Error while trying to get chat ids for chat {chat_id}')
            self.log.error(e, exc_info=True)

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(
                    SendMessageErrorResponse(
                        error_message=f'{str(e)}',
                        error_code='UNKNOWN_ERROR'
                    )
                )
            )

    async def send_typing(self, chat_id: str) -> Response:
        self.log.info(f'Sending typing action for chat id {chat_id}')

        await self.pyrogram_client.send_chat_action(chat_id=chat_id, action=enums.ChatAction.TYPING)

        return Response(status_code=status.HTTP_200_OK)

    async def stop_typing(self, chat_id: str) -> Response:
        self.log.info(f'Stopping typing action for chat id {chat_id}')

        await self.pyrogram_client.send_chat_action(chat_id=chat_id, action=enums.ChatAction.CANCEL)

        return Response(status_code=status.HTTP_200_OK)
