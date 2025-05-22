import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TOKEN: str

    EMAIL_ADDRESS: str
    EMAIL_PASSWORD: str
    IMAP_SERVER: str

    DATA_DIRECTORY: str = os.path.abspath(os.path.join(os.path.dirname(__file__), './data'))

    SCHEDULE_URL: str
    REQ_HEADERS: dict


    class Config:
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))
        env_file_encoding = "utf-8"

settings = Settings()
