import logging
import shutil
import subprocess
import zipfile
from functools import wraps
from os import scandir, walk
from pathlib import Path
from typing import Optional, Callable, Any
import requests
import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, Form, File, Header
from pyngrok import ngrok
from starlette.responses import FileResponse

from .config import PATH, SET_NGROK_IP, store_keeper
from .exceptions import ServerError, TokenRequired


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
def list_files(path: Path, token: Optional[str] = Header(default='')):
    if not path.exists() or not path.is_dir():
        raise HTTPException(status_code=404, detail="Path not found")
    logger.info(f"Sent list of files in {path}")
    files = []
    dirs = []
    for entity in scandir(str(path)):
        entity_dict = {"name": entity.name, "size": entity.stat().st_size, "modification_time": entity.stat().st_mtime}
        if (path / entity.name).is_dir():
            dirs.append(entity_dict)
        else:
            files.append(entity_dict)
    return {"dirs": dirs, "files": files}


@app.get('/file/download')
@token_required
def download_file(path: Path, token: Optional[str] = Header(default='')):
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
def upload_file(file: UploadFile = File(), destination: Optional[Path] = Form(None),
                token: Optional[str] = Header(default='')):
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
def execute_cmd(command: str, token: Optional[str] = Header(default='')):
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
    def __init__(self, port: int = 8000, require_token: Optional[str] = None) -> None:
        require_token = '' if require_token is None else require_token
        global secure_token
        self.port = port
        secure_token = require_token
        try:
            ngrok_token = store_keeper.get_value("ngrok_token")
            ngrok.set_auth_token(ngrok_token)
        except KeyError:
            logger.warning("Ngrok token not found in config.json")
        self.ngrok_ip = ""

    def _post_ngrok_ip(self) -> None:
        token = store_keeper.get_token()
        if token is None:
            raise TokenRequired()
        json = {"token": token, "ngrok_ip": self.ngrok_ip}
        try:
            response = requests.post(f'http://{PATH}{SET_NGROK_IP}', json=json)
        except Exception as e:
            raise ServerError(e)
        if response.status_code != 200:
            message = response.headers['message'] if 'message' in response.headers else ''
            raise ServerError(f"{response.status_code} {message}")
        else:
            logger.debug(f"Successful set ngrok ip")

    def run(self) -> None:
        self.ngrok_ip = ngrok.connect(self.port).public_url
        logger.info(f"Ngrok ip: {self.ngrok_ip}")
        try:
            self._post_ngrok_ip()
        except ServerError as e:
            print(f"Server error due setting ngrok ip {e.args}")
            print("Local host mode")
            logger.info(f"Server error due setting ngrok ip {e.args}")

        uvicorn.run("filesocket.managed_device_client:app", port=self.port, reload=False, log_level="info")
        logger.debug(f"Connection closed")
