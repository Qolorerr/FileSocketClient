import logging
import shutil
import zipfile
from pathlib import Path
from typing import Optional
from os import walk
import requests

from .config import PATH, GET_NGROK_IP, NGROK_CHECK_ONLINE, NGROK_CMD_COMMAND, NGROK_UPLOAD_FILE, NGROK_DOWNLOAD_FILE, \
    NGROK_LIST_FILES
from .exceptions import ServerError, PathNotFoundError
from .storekeeper import Storekeeper


DOWNLOADS_PATH = Path.home() / "Downloads"


class ManagingClient:
    def __init__(self, store_keeper: Storekeeper, device_id: str, device_secure_token: str = ''):
        self.store_keeper = store_keeper
        self.device_id = device_id
        self.default_header = {'token': device_secure_token}
        self.device_ngrok_ip = None
        self.logger = logging.getLogger("managing")

    # Check is other PC client is online
    def check_online(self) -> bool:
        try:
            response = requests.get(f'{self.device_ngrok_ip}{NGROK_CHECK_ONLINE}')
        except Exception as e:
            raise ServerError(e)
        return response.status_code == 200

    # Execute any CMD command on another PC
    def cmd_command(self, command: str) -> Optional[dict]:
        if command == '':
            return None
        try:
            response = requests.get(f'{self.device_ngrok_ip}{NGROK_CMD_COMMAND}?command={command}',
                                    headers=self.default_header)
        except Exception as e:
            raise ServerError(e)
        return response.json()

    # Send any file or folder to another PC
    def send_file(self, path: Path, destination: Path = Path('')) -> None:
        if not path.exists():
            raise PathNotFoundError
        if str(destination) == '.':
            destination = None

        if path.is_file():
            files = {'file': open(path, 'rb')}
        else:
            zip_file_path = DOWNLOADS_PATH / (path.name + '.zip')
            with zipfile.ZipFile(zip_file_path, "w") as zip_file:
                for root, dirs, files in walk(path):
                    for file in files:
                        zip_file.write(Path(root) / file)
            files = {'file': open(zip_file_path, 'rb')}
        destination_data = dict()
        if destination is not None:
            destination_data['destination'] = str(destination)
        try:
            response = requests.post(f"{self.device_ngrok_ip}{NGROK_UPLOAD_FILE}",
                                     files=files, headers=self.default_header, data=destination_data)
        except Exception as e:
            raise ServerError(e)
        if response.status_code != 200:
            response_json = response.json()
            message = response_json['detail'] if 'detail' in response_json else ''
            raise ServerError(f"{response.status_code} {message}")

    # Get file or folder from another PC
    def get_file(self, path: Path, destination: Optional[Path] = Path('')) -> None:
        if str(destination) != '.' and not destination.exists():
            raise PathNotFoundError
        if str(destination) == '.':
            destination = DOWNLOADS_PATH
        try:
            response = requests.get(f"{self.device_ngrok_ip}{NGROK_DOWNLOAD_FILE}"
                                    f"?path={str(path)}", headers=self.default_header, stream=True)
        except Exception as e:
            raise ServerError(e)

        if response.status_code != 200:
            response_json = response.json()
            message = response_json['detail'] if 'detail' in response_json else ''
            raise ServerError(f"{response.status_code} {message}")

        if not destination.is_file():
            destination /= response.headers['Content-Disposition'].split('; ')[-1]\
                .removeprefix('filename="').removesuffix('"')
        try:
            with destination.open("wb") as buffer:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, buffer)
        except Exception as e:
            raise IOError(e)

    def list_files(self, path: Path) -> Optional[dict]:
        try:
            response = requests.get(f'{self.device_ngrok_ip}{NGROK_LIST_FILES}?path={path}',
                                    headers=self.default_header)
        except Exception as e:
            raise ServerError(e)
        if response.status_code != 200:
            response_json = response.json()
            message = response_json['detail'] if 'detail' in response_json else ''
            raise ServerError(f"{response.status_code} {message}")
        return response.json()

    def _user_interface(self):
        while True:
            try:
                if not self.check_online():
                    print("PC offline")
                    break
            except ServerError as e:
                self.logger.info(f"Server error {e.args}")
                break

            print("Available actions:")
            print("1) Send cmd command")
            print("2) Send file")
            print("3) Download file")
            print("4) List files in path")
            print("0) Close")
            ans = input().strip()
            try:
                if ans == '1':
                    command = input("Cmd command: ").strip()
                    cmd_response = self.cmd_command(command)
                    self.logger.debug(f"Got cmd response, data: {cmd_response}")
                    for key, value in cmd_response.items():
                        print(f"Result: cmd -> {key}: {value}\n")
                elif ans == '2':
                    path = Path(input("File path: ").strip())
                    destination = Path(input("Destination path: ").strip())
                    self.send_file(path, destination)
                    self.logger.debug(f"Sent file (dir): {path}")
                elif ans == '3':
                    path = Path(input("File path: ").strip())
                    destination = Path(input("Destination path: ").strip())
                    self.get_file(path, destination)
                    self.logger.debug(f"Got file (dir): {destination}")
                elif ans == '4':
                    path = Path(input("File path: ").strip())
                    list_files_response = self.list_files(path)
                    self.logger.debug(f"Got list files response, data: {list_files_response}")
                    if list_files_response is not None:
                        print(*sorted(list_files_response['dirs']), sep='\n')
                        print(*sorted(list_files_response['files']), sep='\n')
                elif ans == '0':
                    print("Bye")
                    break
                else:
                    continue
            except ServerError as e:
                print(f"Server error {e.args}")
                self.logger.info(f"Server error {e.args}")
            except PathNotFoundError:
                print("Path does not exist")
                self.logger.info("Path does not exist")
            except IOError as e:
                print(f"File saving error {e.args}")
                self.logger.info(f"File saving error {e.args}")

    def _get_ngrok_ip(self) -> None:
        token = self.store_keeper.get_token()
        json = {"device_id": self.device_id, "token": token}
        try:
            response = requests.get(f'http://{PATH}{GET_NGROK_IP}', json=json)
        except Exception as e:
            raise ServerError(e)
        json = response.json()
        if response.status_code == 200 and 'ngrok_ip' in json:
            self.logger.debug(f"Got new device ngrok ip")
            self.device_ngrok_ip = json['ngrok_ip']
        else:
            message = response.headers['message'] if 'message' in response.headers else ''
            raise ServerError(f"Can't get ngrok ip: {response.status_code} {message}\n")

    def run(self) -> None:
        try:
            self._get_ngrok_ip()
        except ServerError as e:
            print(f"Server error {e.args}")
            self.logger.info(f"Server error {e.args}")
            return
        self._user_interface()