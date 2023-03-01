import logging
import os

import pydantic
import yaml
from pydantic import BaseModel, Field


class ProgramArguments(BaseModel):
    log_level: str = Field('INFO', alias='SERVER_LOG_LEVEL', min_length=1)
    bot_token: str = Field(alias='BOT_TOKEN', min_length=1)
    api_hash: str = Field(alias='API_HASH', min_length=1)
    api_id: str = Field(alias='API_ID', min_length=1)


def parse_arguments() -> ProgramArguments:
    try:
        return ProgramArguments(
            log_level=os.environ.get('SERVER_LOG_LEVEL'),
            bot_token=os.environ.get('BOT_TOKEN'),
            api_hash=os.environ.get('API_HASH'),
            api_id=os.environ.get('API_ID'),
        )
    except pydantic.error_wrappers.ValidationError as e:
        print(e)


arguments = parse_arguments()

# Configure logging
with open('logging.yaml') as fp:
    conf = yaml.load(fp, Loader=yaml.FullLoader)

conf['root']['level'] = arguments.log_level

logging.config.dictConfig(conf)

log = logging.getLogger(f'{__name__}.main')
