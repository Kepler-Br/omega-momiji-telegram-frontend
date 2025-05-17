import logging
import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import Message as PyrogramMessage, User, Chat

from src.prometheus_metrics import prometheus_frontend_messages_media, \
    prometheus_frontend_messages_service, prometheus_frontend_messages_text, prometheus_frontend_messages_caption, \
    prometheus_frontend_messages_document, prometheus_frontend_messages_forwards, \
    prometheus_frontend_messages_group_chat_created, prometheus_frontend_messages_left_chat_members, \
    prometheus_frontend_messages_location, prometheus_frontend_messages_new_chat_members, \
    prometheus_frontend_messages_new_chat_photo, prometheus_frontend_messages_new_chat_title, \
    prometheus_frontend_messages_photo, prometheus_frontend_messages_pinned_message, prometheus_frontend_messages_poll, \
    prometheus_frontend_messages_reactions, prometheus_frontend_messages_sticker, \
    prometheus_frontend_messages_supergroup_chat_created, prometheus_frontend_messages_video_chat_ended, \
    prometheus_frontend_messages_video_chat_started, prometheus_frontend_messages_video, \
    prometheus_frontend_messages_video_note, prometheus_frontend_messages_voice, \
    prometheus_frontend_known_private_chats, prometheus_frontend_known_group_chats, \
    prometheus_frontend_known_supergroup_chats, prometheus_frontend_known_channel_chats, \
    prometheus_frontend_known_bot_chats, prometheus_frontend_known_unknown_chats, prometheus_frontend_known_users, \
    prometheus_frontend_messages


def register_prometheus_handler(client: Client, group: int = -458155):
    log = logging.getLogger(f'{__name__}.register_prometheus_handler')

    known_private_chats: set[int] = set()
    known_group_chats: set[int] = set()
    known_supergroup_chats: set[int] = set()
    known_bot_chats: set[int] = set()
    known_channel_chats: set[int] = set()
    known_unknown_chats: set[int] = set()

    known_users: set[int] = set()

    async def __prometheus_handler(_: Client, pyrogram_message: PyrogramMessage):
        prometheus_frontend_messages.inc()
        if pyrogram_message.chat.type == ChatType.PRIVATE:
            known_private_chats.add(pyrogram_message.chat.id)
            prometheus_frontend_known_private_chats.set(len(known_private_chats))
        elif pyrogram_message.chat.type == ChatType.GROUP:
            known_group_chats.add(pyrogram_message.chat.id)
            prometheus_frontend_known_group_chats.set(len(known_group_chats))
        elif pyrogram_message.chat.type == ChatType.SUPERGROUP:
            known_supergroup_chats.add(pyrogram_message.chat.id)
            prometheus_frontend_known_supergroup_chats.set(len(known_supergroup_chats))
        elif pyrogram_message.chat.type == ChatType.CHANNEL:
            known_channel_chats.add(pyrogram_message.chat.id)
            prometheus_frontend_known_channel_chats.set(len(known_channel_chats))
        elif pyrogram_message.chat.type == ChatType.BOT:
            known_bot_chats.add(pyrogram_message.chat.id)
            prometheus_frontend_known_bot_chats.set(len(known_bot_chats))
        else:
            known_unknown_chats.add(pyrogram_message.chat.id)
            prometheus_frontend_known_unknown_chats.set(len(known_unknown_chats))

        if pyrogram_message.from_user is None:
            log.error("pyrogram_message.from_user is not set")
        elif pyrogram_message.from_user.id not in known_users:
            known_users.add(pyrogram_message.from_user.id)
            prometheus_frontend_known_users.set(len(known_users))

        if pyrogram_message.caption is not None:
            prometheus_frontend_messages_caption.inc()
        if pyrogram_message.document is not None:
            prometheus_frontend_messages_document.inc()
        if pyrogram_message.forwards is not None:
            prometheus_frontend_messages_forwards.inc()
        if pyrogram_message.group_chat_created is not None:
            prometheus_frontend_messages_group_chat_created.inc()
        if pyrogram_message.left_chat_member is not None:
            prometheus_frontend_messages_left_chat_members.inc()
        if pyrogram_message.location is not None:
            prometheus_frontend_messages_location.inc()
        if pyrogram_message.media is not None:
            prometheus_frontend_messages_media.inc()
        if pyrogram_message.new_chat_members is not None:
            prometheus_frontend_messages_new_chat_members.inc()
        if pyrogram_message.new_chat_photo is not None:
            prometheus_frontend_messages_new_chat_photo.inc()
        if pyrogram_message.new_chat_title is not None:
            prometheus_frontend_messages_new_chat_title.inc()
        if pyrogram_message.photo is not None:
            prometheus_frontend_messages_photo.inc()
        if pyrogram_message.pinned_message is not None:
            prometheus_frontend_messages_pinned_message.inc()
        if pyrogram_message.poll is not None:
            prometheus_frontend_messages_poll.inc()
        if pyrogram_message.reactions is not None:
            prometheus_frontend_messages_reactions.inc()
        if pyrogram_message.service is not None:
            prometheus_frontend_messages_service.inc()
        if pyrogram_message.sticker is not None:
            prometheus_frontend_messages_sticker.inc()
        if pyrogram_message.supergroup_chat_created is not None:
            prometheus_frontend_messages_supergroup_chat_created.inc()
        if pyrogram_message.text is not None:
            prometheus_frontend_messages_text.inc()
        if pyrogram_message.video_chat_ended is not None:
            prometheus_frontend_messages_video_chat_ended.inc()
        if pyrogram_message.video_chat_started is not None:
            prometheus_frontend_messages_video_chat_started.inc()
        if pyrogram_message.video is not None:
            prometheus_frontend_messages_video.inc()
        if pyrogram_message.video_note is not None:
            prometheus_frontend_messages_video_note.inc()
        if pyrogram_message.voice is not None:
            prometheus_frontend_messages_voice.inc()

    client.add_handler(pyrogram.handlers.MessageHandler(__prometheus_handler, filters=None), group=group)
