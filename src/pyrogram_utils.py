from typing import Optional

from pyrogram import types


def get_fullname(user: types.User) -> Optional[str]:
    if user.first_name is None and user.last_name is None:
        return None

    if user.first_name is not None and user.last_name is None:
        return user.first_name

    if user.first_name is None and user.last_name is not None:
        return user.last_name

    return f'{user.first_name} {user.last_name}'
