import json

from pyrogram.types import Message

mock_usernames = [
    'nightly_user',
    'daily_user',
    'annually_user',
]

mock_titles = [
    'Omega Group',
    'Lovers Of Greek Alphabet Pronunciations',
    'Shrek Film Lovers',
]

mock_first_name = [
    'John',
    'Samantha',
    'Elize',
]

mock_last_name = [
    'Johnson',
    'Samanthason',
    'Elizason',
]


def print_constructor_recursive(d: dict):
    object_type = d['_']
    print(f'{object_type}(')
    for key in d:
        if key == '_':
            continue
        if isinstance(d[key], str):
            if key == 'last_name':
                processed = f'\'{mock_last_name.pop()}\''
            elif key == 'username':
                processed = f'\'{mock_usernames.pop()}\''
            elif key == 'title':
                processed = f'\'{mock_titles.pop()}\''
            elif key == 'first_name':
                processed = f'\'{mock_first_name.pop()}\''
            elif key == 'date':
                processed = 'datetime.datetime.now()'
            elif key in {'type', 'media', 'status'}:
                processed = d[key]
            else:
                processed = f'\'{d[key]}\''

            print(f'{key}={processed},')
        elif isinstance(d[key], int):
            if key == 'id':
                processed = (d[key] * 35742549198872617291353508656626642567) % 27644437
            else:
                processed = d[key]
            print(f'{key}={processed},')
        elif isinstance(d[key], dict):
            print(f'{key}=', end='')
            print_constructor_recursive(d[key])
        elif isinstance(d[key], list):
            if isinstance(d[key][0], dict):
                print(f'{key}=', end='')
                print('[')
                for it in d[key]:
                    print_constructor_recursive(it)
                print(']')
            else:
                print(f'{key}={d[key]},')
        else:
            print('Unknown')
    print('),')


def print_constructor(message: Message):
    print_constructor_recursive(json.loads(message.__str__()))
