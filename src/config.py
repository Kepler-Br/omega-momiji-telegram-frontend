from typing import List

from pydantic import BaseModel, Field

from src.tools import get_dict_key_by_path, convert_string_size_to_bytes


class S3Config(BaseModel):
    url: str = Field(min_length=1)

    class Config:
        validate_by_name = True


class KafkaConfig(BaseModel):
    bootstrap_servers: str = Field(min_length=1)
    messages_topic: str = Field(min_length=1)


class FrontendConfig(BaseModel):
    name: str = Field(min_length=1)
    max_file_size: int = Field()
    upload_files: bool = Field(default=True)
    whitelist: List[int] = Field()


def get_configurations(conf: dict) -> tuple[S3Config, KafkaConfig, FrontendConfig]:
    s3_config = S3Config(url=get_dict_key_by_path(conf, 's3.url'))
    kafka_config = KafkaConfig(
        bootstrap_servers=get_dict_key_by_path(conf, 'kafka.bootstrap.servers'),
        messages_topic=get_dict_key_by_path(conf, 'kafka.messages.topic'),
    )
    frontend_config = FrontendConfig(
        name=get_dict_key_by_path(conf, 'frontend.name'),
        max_file_size=convert_string_size_to_bytes(get_dict_key_by_path(conf, 'frontend.max-file-size')),
        upload_files=get_dict_key_by_path(conf, 'frontend.upload-files', fail=False),
        whitelist=get_dict_key_by_path(conf, 'frontend.chat.whitelist'),
    )

    return s3_config, kafka_config, frontend_config
