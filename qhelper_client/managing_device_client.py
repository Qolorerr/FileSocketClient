import json
import logging
import sys
import rel
import websocket
from websocket import WebSocketApp

from .config import PATH, WS_CONNECT_PATH
from .storekeeper import Storekeeper


class ManagingClient:
    def __init__(self, store_keeper: Storekeeper, device_id: str):
        self.store_keeper = store_keeper
        self.device_id = device_id
        self.logger = logging.getLogger("managing")

    def _send_message(self, ws: WebSocketApp):
        while True:
            answer_data = {}
            print("Available actions:\n")
            print("1) Send cmd command\n")
            print("0) Close connection\n")
            ans = input().strip()
            if ans == '1':
                answer_data['commands'] = {}
                ans = input("Command: ").strip()
                if ans == '':
                    continue
                answer_data['commands']['cmd'] = ans
            elif ans == '0':
                ws.close(status=1000)
                self.logger.debug(f"Connection closed")
                sys.exit()
            else:
                continue
            ws.send(json.dumps(answer_data))
            self.logger.debug(f"Sent message, data: {answer_data}")
            break

    # TODO: Logger
    def _on_message(self, ws: WebSocketApp, message: str) -> None:
        data = json.loads(message)
        sender_info = f"{data['sender_details']['type']}{data['sender_details']['id']} {data['sender_details']['name']}"
        if 'results' in data:
            if 'cmd' in data['results']:
                self.logger.debug(f"Got response, data: {data['results']['cmd']}")
                for key, value in data['results']['cmd'].items():
                    print(f"Result from {sender_info}: cmd -> {key}: {value}\n")
        self._send_message(ws)

    def _on_error(self, ws: WebSocketApp, error: Exception) -> None:
        self.logger.info(f"Server error {error}")
        print(f"Server error {error}\n")

    def _on_close(self, ws: WebSocketApp, close_status_code: int, close_msg: str) -> None:
        self.logger.debug(f"Connection closed")
        print("Connection closed\n")

    def on_open(self, ws: WebSocketApp):
        self._send_message(ws)

    def run(self) -> None:
        # websocket.enableTrace(True)
        token = self.store_keeper.get_token()
        if token is None:
            print("Token is required\n")
            return
        ws = websocket.WebSocketApp(f"ws://{PATH}{WS_CONNECT_PATH}",
                                    on_open=self.on_open,
                                    on_message=self._on_message,
                                    on_error=self._on_error,
                                    on_close=self._on_close,
                                    header={'token': token, 'device_id': self.device_id})

        ws.run_forever(dispatcher=rel)
        rel.signal(2, rel.abort)
        rel.dispatch()
        self.logger.debug(f"Connection closed")
