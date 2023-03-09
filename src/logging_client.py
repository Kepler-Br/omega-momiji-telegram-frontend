import dataclasses
import logging
from datetime import datetime
from typing import Union, List, Optional

import aiohttp
import pyrogram
from pyrogram import Client, types, enums
from pyrogram.enums import MessageServiceType
from pyrogram.session import Session
from pyrogram.types import Message as PyrogramMessage

from new_message_request import NewMessageUser, NewMessageChat, ChatType, NewMessageRequest, MessageType, ActionType, \
    NewMessageActionInfo
from pyrogram_utils import get_fullname


def get_action_related_user(value: PyrogramMessage) -> NewMessageUser:
    if value.left_chat_member is not None:
        return NewMessageUser(
            id=str(value.left_chat_member.id),
            username=value.left_chat_member.username,
            fullname=get_fullname(value.left_chat_member),
        )
    elif value.new_chat_members is not None:
        new_chat_member = value.new_chat_members[0]

        return NewMessageUser(
            id=str(new_chat_member.id),
            username=new_chat_member.username,
            fullname=get_fullname(new_chat_member),
        )

    raise RuntimeError("Unknown action type for related user")


def get_action_type(value: PyrogramMessage) -> str:
    if value.service == MessageServiceType.NEW_CHAT_MEMBERS:
        return ActionType.NEW_MEMBER
    elif value.service == MessageServiceType.LEFT_CHAT_MEMBERS:
        return ActionType.MEMBER_LEFT
    else:
        return ActionType.OTHER


def get_message_type(value: PyrogramMessage) -> str:
    if value.service == MessageServiceType.LEFT_CHAT_MEMBERS or value.service == MessageServiceType.NEW_CHAT_MEMBERS:
        return MessageType.ACTION
    if value.service is not None:
        return MessageType.OTHER
    return MessageType.MESSAGE


class LoggingClient(Client):
    def __init__(
            self,
            name: str,
            message_gateway_addresses: list[str],
            frontend_name: str,
            api_id: Union[int, str] = None,
            api_hash: str = None,
            app_version: str = Client.APP_VERSION,
            device_model: str = Client.DEVICE_MODEL,
            system_version: str = Client.SYSTEM_VERSION,
            lang_code: str = Client.LANG_CODE,
            ipv6: bool = False,
            proxy: dict = None,
            test_mode: bool = False,
            bot_token: str = None,
            session_string: str = None,
            in_memory: bool = None,
            phone_number: str = None,
            phone_code: str = None,
            password: str = None,
            workers: int = Client.WORKERS,
            workdir: str = Client.WORKDIR,
            plugins: dict = None,
            parse_mode: enums.ParseMode = enums.ParseMode.DEFAULT,
            no_updates: bool = None,
            takeout: bool = None,
            sleep_threshold: int = Session.SLEEP_THRESHOLD,
            hide_password: bool = False
    ):
        super().__init__(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            app_version=app_version,
            device_model=device_model,
            system_version=system_version,
            lang_code=lang_code,
            ipv6=ipv6,
            proxy=proxy,
            test_mode=test_mode,
            bot_token=bot_token,
            session_string=session_string,
            in_memory=in_memory,
            phone_number=phone_number,
            phone_code=phone_code,
            password=password,
            workers=workers,
            workdir=workdir,
            plugins=plugins,
            parse_mode=parse_mode,
            no_updates=no_updates,
            takeout=takeout,
            sleep_threshold=sleep_threshold,
            hide_password=hide_password,
        )
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self._message_gateway_addresses = message_gateway_addresses
        self._frontend_name = frontend_name

        self.add_handler(pyrogram.handlers.MessageHandler(self._gateway_log_handler, filters=None), group=-999)
        self.add_handler(pyrogram.handlers.MessageHandler(self._log_handler, filters=None), group=-998)

    async def _log_handler(self, client, pyrogram_message: PyrogramMessage):
        result = f'Incoming message: {pyrogram_message.id}\n'
        # Chat info
        if pyrogram_message.chat.title is not None:
            result += f'From chat: {pyrogram_message.chat.title} ({pyrogram_message.chat.id})\n'
        else:
            fullname = pyrogram_message.chat.first_name + pyrogram_message.chat.last_name if pyrogram_message.chat.last_name else ''
            result += f'From chat: @{pyrogram_message.chat.username} "{fullname}" ({pyrogram_message.chat.id})\n'

        # User info
        result += f'From user: @{pyrogram_message.from_user.username} "{pyrogram_message.from_user.first_name} {pyrogram_message.from_user.last_name}" ({pyrogram_message.from_user.id})\n'

        # Media
        if pyrogram_message.media is not None:
            result += f'Media: {pyrogram_message.media.name}\n'

        # Service
        if pyrogram_message.service is not None:
            result += f'Service: {pyrogram_message.service.name}\n'

        # Text
        if pyrogram_message.text is not None:
            result += f'Text: {pyrogram_message.text}\n'

        # Caption
        if pyrogram_message.caption is not None:
            result += f'Caption: {pyrogram_message.caption}\n'

        self.log.info(result.strip())

    async def _gateway_log_handler(self, client, pyrogram_message: PyrogramMessage):
        author = NewMessageUser(
            id=str(pyrogram_message.from_user.id),
            username=pyrogram_message.from_user.username,
            fullname=get_fullname(pyrogram_message.from_user),
        )
        chat = NewMessageChat(
            id=str(pyrogram_message.id),
            title=pyrogram_message.chat.title,
            type=ChatType.GROUP if pyrogram_message.chat.id < 0 else ChatType.PRIVATE,
        )
        message_type = get_message_type(pyrogram_message)
        action_info = None
        if message_type == MessageType.ACTION:
            action_info = NewMessageActionInfo(
                action_type=get_action_type(pyrogram_message),
                related_user=get_action_related_user(pyrogram_message),
            )
        message = NewMessageRequest(
            id=str(pyrogram_message.id),
            author=author,
            chat=chat,
            frontend=self._frontend_name,
            text=pyrogram_message.text,
            type=message_type,
            action_info=action_info
        )

        for gateway_address in self._message_gateway_addresses:
            async with aiohttp.ClientSession() as session:
                try:
                    response = await session.put(
                        f'{gateway_address}/inbound/messages',
                        json=dataclasses.asdict(message)
                    )

                    status = response.status
                    if status != 200:
                        self.log.error(
                            f'Unexpected answer from gateway "{gateway_address}"\n'
                            f'Status: {status}\n'
                            f'Body:{await response.text()}')
                except RuntimeError as e:
                    self.log.error(
                        f'Exception raised while sending new message to gateway "{gateway_address}":'
                    )
                    self.log.error(e, exc_info=True)
                finally:
                    await session.close()

    async def send_message(
            self: pyrogram.Client,
            chat_id: Union[int, str],
            text: str,
            parse_mode: Optional[enums.ParseMode] = None,
            entities: List[types.MessageEntity] = None,
            disable_web_page_preview: bool = None,
            disable_notification: bool = None,
            reply_to_message_id: int = None,
            schedule_date: datetime = None,
            protect_content: bool = None,
            reply_markup: Union[
                types.InlineKeyboardMarkup,
                types.ReplyKeyboardMarkup,
                types.ReplyKeyboardRemove,
                types.ForceReply
            ] = None
    ) -> types.Message:
        return await super().send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            schedule_date=schedule_date,
            protect_content=protect_content,
            reply_markup=reply_markup,
        )
