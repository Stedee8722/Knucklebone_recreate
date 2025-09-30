import os, colorlog, logging
from dotenv import load_dotenv
from logging.config import dictConfig

load_dotenv()

TOKEN = os.getenv("TOKEN")

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            '()': 'colorlog.ColoredFormatter',
            "format": "[%(asctime)s] [%(filename)s/%(log_color)s%(levelname)s%(reset)s] [%(module)s]: %(message)s",
            "datefmt": "%d/%m %H:%M:%S",
            "reset": True,
            "log_colors": {
                'DEBUG':    'white',
                'INFO':     'light_green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
	        },
        },
        "standard": {
            '()': 'colorlog.ColoredFormatter',
            "format": "[%(asctime)s] [%(filename)s/%(log_color)s%(levelname)s%(reset)s] [%(name)s]: %(message)s",
            "datefmt": "%d/%m %H:%M:%S",
            "reset": True,
            "log_colors": {
                'DEBUG':    'white',
                'INFO':     'light_green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
	        },
        },
        "file": {
            "format": "[%(asctime)s] [%(filename)s/%(levelname)s] [%(module)s]: %(message)s",
            "datefmt": "%d/%m %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "Logs/log.log",
            "mode": "a",
            "formatter": "file",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
        "exception": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)