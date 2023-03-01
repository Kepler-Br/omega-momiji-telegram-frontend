import logging
from datetime import datetime
from typing import Union, List, Optional

import pyrogram
from pyrogram import Client, types, enums
from pyrogram.session import Session
from pyrogram.types import Message as PyrogramMessage


class LoggingClient(Client):
    def __init__(
            self,
            name: str,
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

        async def func(client, pyrogram_message: PyrogramMessage):
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

        self.add_handler(pyrogram.handlers.MessageHandler(func, filters=None), group=-999)

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
