import json
import os
from logging.config import dictConfig
from typing import Optional

from .config import CONFIG_FILE, LOGGER_CONFIG

TOKEN_KEY = 'token'


class Storekeeper:
    def __init__(self):
        dictConfig(LOGGER_CONFIG)

    @staticmethod
    def init() -> None:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({}, f, indent=2)

    @staticmethod
    def check_existence():
        return os.path.exists(CONFIG_FILE)

    def _get_json(self) -> dict:
        if self.check_existence():
            with open(CONFIG_FILE) as f:
                data = json.load(f)
        else:
            data = dict()
        return data

    def add_value(self, key: str, value) -> None:
        data = self._get_json()
        data[key] = value
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def add_token(self, token: str) -> None:
        self.add_value(TOKEN_KEY, token)

    def get_token(self) -> Optional[str]:
        data = self._get_json()
        return data[TOKEN_KEY] if TOKEN_KEY in data else None
