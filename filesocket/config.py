import os

PATH = os.environ.get('FileSocketServer', "127.0.0.1:5000")
SIGN_UP_PATH = "/filesocket/signup"
GET_TOKEN_PATH = "/filesocket/get_token"
GET_NGROK_IP = "/filesocket/get_ngrok_ip"
SET_NGROK_IP = "/filesocket/set_ngrok_ip"
SHOW_ALL_PC_PATH = "/filesocket/show_all_pc"

NGROK_CHECK_ONLINE = "/"
NGROK_CMD_COMMAND = "/cmd"
NGROK_UPLOAD_FILE = "/file/upload"
NGROK_DOWNLOAD_FILE = "/file/download"
NGROK_LIST_FILES = "/file/list"

DEVICE_TYPE = "pc"

CONFIG_FILE = "config.json"
ERROR_LOG_FILENAME = "error.log"
RECEIVED_COMMANDS_LOG = "commands.log"

LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s:%(name)s:%(process)d:%(lineno)d %(levelname)s %(module)s.%(funcName)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[%(levelname)s] in %(module)s.%(funcName)s: %(message)s",
        },
    },
    "handlers": {
        "error_logfile": {
            "formatter": "default",
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": ERROR_LOG_FILENAME,
            "backupCount": 2,
        },
        "command_logfile": {
            "formatter": "default",
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": RECEIVED_COMMANDS_LOG,
            "backupCount": 2,
        },
        "verbose_output": {
            "formatter": "simple",
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "app": {
            "level": "INFO",
            "handlers": [
                "verbose_output",
            ],
        },
        "managed": {
            "level": "INFO",
            "handlers": [
                "verbose_output",
                "command_logfile",
            ],
        },
        "managing": {
            "level": "INFO",
            "handlers": [
                "verbose_output",
            ],
        },
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "error_logfile"
        ]
    },
}
