import json
import os
from logging.config import dictConfig
from typing import Optional


class Storekeeper:
    def __init__(self, logger_config: dict, config_file: str):
        dictConfig(logger_config)
        self.config_file = config_file

    def init(self) -> None:
        with open(self.config_file, 'w') as f:
            json.dump({}, f, indent=2)

    def check_existence(self):
        return os.path.exists(self.config_file)

    def _get_json(self) -> dict:
        if self.check_existence():
            with open(self.config_file) as f:
                data = json.load(f)
        else:
            data = dict()
        return data

    def add_value(self, key: str, value) -> None:
        data = self._get_json()
        data[key] = value
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_value(self, key: str):
        data = self._get_json()
        try:
            return data[key]
        except KeyError:
            raise KeyError("JSON key not found")

    def add_token(self, token: str) -> None:
        self.add_value("token", token)

    def get_token(self) -> Optional[str]:
        data = self._get_json()
        return data["token"] if "token" in data else None
