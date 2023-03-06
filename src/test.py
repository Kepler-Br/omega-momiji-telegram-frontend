import dataclasses
import json
import logging

import aiohttp

from new_message_request import NewMessageAuthor, NewMessageChat, NewMessageRequest, ChatType


async def test_send(gateway_address: str, frontend_name: str = 'telegram'):
    log = logging.getLogger(f'{__name__}.test_send')

    author = NewMessageAuthor(
        id='NewMessageAuthor',
        username='username',
        fullname='fullname',
    )
    chat = NewMessageChat(
        id='NewMessageChat',
        title='title',
        type=ChatType.PRIVATE,
    )
    message = NewMessageRequest(
        id='NewMessageRequest',
        author=author,
        chat=chat,
        frontend=frontend_name,
        text='text',
    )

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
