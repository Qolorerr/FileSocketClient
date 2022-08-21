import json
import logging
import subprocess
import sys
import rel
import requests
import websocket
from websocket import WebSocketApp

from .config import PATH, CHANGE_ACTIVE_MODE_PATH, WS_CONNECT_PATH
from .storekeeper import Storekeeper


class ManagedClient:
    def __init__(self, store_keeper: Storekeeper):
        self.store_keeper = store_keeper
        self.logger = logging.getLogger("managed")

    def _change_active_mode(self, new_active_mode: bool) -> None:
        token = self.store_keeper.get_token()
        json = {"token": token, "is_active": new_active_mode}
        try:
            response = requests.post(f'http://{PATH}{CHANGE_ACTIVE_MODE_PATH}', json=json)
        except Exception as e:
            self.logger.info(f"Server error {e}")
            print(f"Server error {e}\n")
            sys.exit()
        if response.status_code != 200:
            message = response.headers['message'] if 'message' in response.headers else ''
            self.logger.info(f"Error due changing active mode, code: {response.status_code}")
            print(f"Error due changing active mode: {response.status_code} {message}\n")
        else:
            self.logger.debug(f"Successful changing active mode")

    def _on_message(self, ws: WebSocketApp, message: str) -> None:
        data = json.loads(message)
        sender_info = f"{data['sender_details']['type']}{data['sender_details']['id']} {data['sender_details']['name']}"
        answer_data = {}
        if 'commands' in data:
            answer_data['results'] = {}
            if 'cmd' in data['commands']:
                self.logger.warning(f"COMMAND cmd {data['commands']['cmd']}, sender: {sender_info}")
                print(f"Command from {sender_info}: cmd {data['commands']['cmd']}\n")
                out, err = subprocess.Popen(data['commands']['cmd'],
                                            shell=True,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE).communicate()
                answer_data['results']['cmd'] = dict()
                if out is not None:
                    answer_data['results']['cmd']['out'] = out.decode('cp866')
                if err is not None:
                    answer_data['results']['cmd']['error'] = err.decode('cp866')
        ws.send(json.dumps(answer_data))

    def _on_error(self, ws: WebSocketApp, error: Exception) -> None:
        self.logger.info(f"Server error {error}")
        print(f"Server error {error}\n")

    def _on_close(self, ws: WebSocketApp, close_status_code: int, close_msg: str) -> None:
        self._change_active_mode(False)
        self.logger.debug(f"Connection closed")
        print("Connection closed\n")

    def run(self) -> None:
        self._change_active_mode(True)
        # websocket.enableTrace(True)
        token = self.store_keeper.get_token()
        if token is None:
            print("Token is required\n")
            return
        ws = websocket.WebSocketApp(f"ws://{PATH}{WS_CONNECT_PATH}",
                                    on_message=self._on_message,
                                    on_error=self._on_error,
                                    on_close=self._on_close,
                                    header={'token': token, 'is_managed': 'True'})
        ws.run_forever(dispatcher=rel)
        rel.signal(2, rel.abort)
        rel.dispatch()
        self._change_active_mode(False)
        self.logger.debug(f"Connection closed")
