from functools import lru_cache
from typing import Any

from pydantic import AnyUrl, BaseSettings


class Settings(BaseSettings):
    mongo_url: Any = "mongodb://localhost:27017/"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
