import logging
import shutil
import subprocess
import sys
import zipfile
from functools import wraps
from os import listdir, walk
from pathlib import Path
from typing import Optional, Callable, Any
import requests
import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, Form, File
from pyngrok import ngrok
from starlette.responses import FileResponse

from qhelper_client.config import PATH, SET_NGROK_IP
from qhelper_client.storekeeper import Storekeeper


DOWNLOADS_PATH = Path.home() / "Downloads"

logger = logging.getLogger("managed")
secure_token = ''

app = FastAPI()


def token_required(func) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if secure_token != '' and ('token' not in kwargs or kwargs['token'] != secure_token):
            return HTTPException(status_code=401, detail="Token required")
        return func(*args, **kwargs)
    return wrapper


@app.get('/')
def is_online() -> dict:
    return {"OK": 200}


@app.get('/file/list')
@token_required
def list_files(path: Path, token: Optional[str] = ''):
    if not path.exists() or not path.is_dir():
        raise HTTPException(status_code=404, detail="Path not found")
    logger.info(f"Sent list of files in {path}")
    files_and_dirs = {file for file in listdir(str(path))}
    dirs = set(filter(lambda file: (path / file).is_dir(), files_and_dirs))
    return {"dirs": list(dirs), "files": list(files_and_dirs - dirs)}


@app.get('/file/download')
@token_required
def download_file(path: Path, token: Optional[str] = ''):
    if not path.exists():
        raise HTTPException(status_code=404, detail="Path not found")
    if path.is_file():
        logger.warning(f"Sent {path}")
        return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data')

    # Download zip file of directory
    zip_file_path = DOWNLOADS_PATH / (path.name + '.zip')
    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        for root, dirs, files in walk(path):
            for file in files:
                zip_file.write(Path(root) / file)
    logger.warning(f"Sent {path}")
    return FileResponse(path=str(zip_file_path), filename=zip_file_path.name, media_type='multipart/form-data')


@app.post("/file/upload")
@token_required
def upload_file(file: UploadFile = File(), destination: Optional[Path] = Form(None), token: Optional[str] = ''):
    if destination is not None and not destination.exists():
        raise HTTPException(status_code=404, detail="Destination not found")
    if destination is None:
        destination = DOWNLOADS_PATH
    if not destination.is_file():
        destination /= file.filename
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()
    logger.warning(f"Got {destination}")
    return {"OK": 200}


@app.get("/cmd")
@token_required
def execute_cmd(command: str, token: Optional[str] = ''):
    logger.warning(f"Executed cmd command {command}")
    out, err = subprocess.Popen(command,
                                shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE).communicate()
    answer_data = dict()
    if out is not None:
        answer_data['out'] = out.decode('cp866')
    if err is not None:
        answer_data['error'] = err.decode('cp866')
    return answer_data


class ManagedClient:
    def __init__(self, store_keeper: Storekeeper, port: int = 8000, require_token: str = '') -> None:
        global secure_token
        self.store_keeper = store_keeper
        self.port = port
        secure_token = require_token
        try:
            ngrok_token = self.store_keeper.get_value("ngrok_token")
            ngrok.set_auth_token(ngrok_token)
        except KeyError:
            logger.warning("Ngrok token not found in config.json")
        self.ngrok_ip = ""

    def _post_ngrok_ip(self) -> None:
        token = self.store_keeper.get_token()
        json = {"token": token, "ngrok_ip": self.ngrok_ip}
        try:
            response = requests.post(f'http://{PATH}{SET_NGROK_IP}', json=json)
        except Exception as e:
            logger.info(f"Server error {e}")
            print(f"Server error {e}\n")
            sys.exit()
        if response.status_code != 200:
            message = response.headers['message'] if 'message' in response.headers else ''
            logger.info(f"Error due set ngrok ip, code: {response.status_code}")
            print(f"Error due set ngrok ip: {response.status_code} {message}\n")
            sys.exit()
        else:
            logger.debug(f"Successful set ngrok ip")

    def run(self) -> None:
        self.ngrok_ip = ngrok.connect(self.port).public_url
        logger.info(f"Ngrok ip: {self.ngrok_ip}")
        self._post_ngrok_ip()

        uvicorn.run("managed_device_client:app", port=self.port, reload=False, log_level="debug")
        logger.debug(f"Connection closed")
