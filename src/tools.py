import re
from typing import Optional, Any

compiled_size_regex = re.compile(r'^(\d+) *(KB|MB|GB|TB|Kb|Mb|Gb|Tb|KiB|MiB|GiB|TiB|Kib|Mib|Gib|Tib)?$')


def convert_string_size_to_bytes(value: str) -> Optional[int]:
    matched = compiled_size_regex.match(value)
    if matched is None:
        return None

    size = int(matched.group(1))
    group = matched.group(2)

    base: int = size
    match group:
        case 'KiB' | 'Kib':
            base = 1024 * size
        case 'MiB' | 'Mib':
            base = (1024 ** 2) * size
        case 'GiB' | 'Gib':
            base = (1024 ** 3) * size
        case 'TiB' | 'Tib':
            base = (1024 ** 4) * size

        case 'KB' | 'Kb':
            base = 1000 * size
        case 'MB' | 'Mb':
            base = (1000 ** 2) * size
        case 'GB' | 'Gb':
            base = (1000 ** 3) * size
        case 'TB' | 'Tb':
            base = (1000 ** 4) * size

        case _:
            return base

    return base


def get_dict_key_by_path(dictionary: dict, path: str, fail: bool = True) -> Optional[Any]:
    try:
        value = dictionary
        for key in path.split('.'):
            value = value[key]
    except KeyError as e:
        if fail:
            raise KeyError(f"Key {path} not found in config file") from e
        else:
            return None
    return value
