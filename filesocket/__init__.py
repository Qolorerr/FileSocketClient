import sys

from .__main__ import store_keeper
from .managed_device_client import ManagedClient
from .managing_device_client import ManagingClient
from .config import PATH
from .config import SIGN_UP_PATH
from .config import GET_TOKEN_PATH
from .config import SET_NGROK_IP
from .config import GET_NGROK_IP
from .config import SHOW_AVAILABLE_PC_PATH
from .config import NGROK_UPLOAD_FILE
from .config import NGROK_CMD_COMMAND
from .config import NGROK_CHECK_ONLINE
from .config import DEVICE_TYPE
from .config import CONFIG_FILE
from .config import ERROR_LOG_FILENAME
from .config import RECEIVED_COMMANDS_LOG
from .config import LOGGER_CONFIG

__all__ = [
    "store_keeper",
    "ManagedClient",
    "ManagingClient",
    "PATH",
    "SIGN_UP_PATH",
    "GET_TOKEN_PATH",
    "CHANGE_ACTIVE_MODE_PATH",
    "SHOW_AVAILABLE_PC_PATH",
    "WS_CONNECT_PATH",
    "DEVICE_TYPE",
    "CONFIG_FILE",
    "ERROR_LOG_FILENAME",
    "RECEIVED_COMMANDS_LOG",
    "LOGGER_CONFIG"
]

sys.path.append('.')
